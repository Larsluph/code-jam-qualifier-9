import typing
from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    scope: typing.Mapping[str, typing.Any]

    receive: typing.Callable[[], typing.Awaitable[object]]
    send: typing.Callable[[object], typing.Awaitable[None]]


class RestaurantManager:
    def __init__(self):
        """Instantiate the restaurant manager.

        This is called at the start of each day before any staff get on
        duty or any orders come in. You should do any setup necessary
        to get the system working before the day starts here; we have
        already defined a staff dictionary.
        """
        self.staff = {}
        self.busy = {}

    async def __call__(self, request: Request):
        """Handle a request received.

        This is called for each request received by your application.
        In here is where most of the code for your system should go.

        :param request: request object
            Request object containing information about the sent
            request to your application.
        """
        request_type = request.scope["type"]

        if request_type == "staff.onduty":
            self.staff[request.scope["id"]] = request
            self.busy[request.scope["id"]] = False

        elif request_type == "staff.offduty":
            del self.staff[request.scope["id"]]

        elif request_type == "order":
            order_speciality = request.scope["speciality"]

            # Select staff that is free and got required speciality
            for free_staff in self.staff.values():
                busy = self.busy[free_staff.scope["id"]]
                if not busy and order_speciality in free_staff.scope["speciality"]:
                    # If so, staff become busy
                    self.busy[free_staff.scope["id"]] = True
                    break

            full_order = await request.receive()
            await free_staff.send(full_order)

            result = await free_staff.receive()
            await request.send(result)

            # order complete, staff not busy anymore
            self.busy[free_staff.scope["id"]] = False
