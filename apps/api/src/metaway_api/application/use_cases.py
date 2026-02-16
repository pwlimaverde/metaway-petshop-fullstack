class BaseUseCase:
    async def execute(self) -> None:
        raise NotImplementedError
