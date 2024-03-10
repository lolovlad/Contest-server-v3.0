from MainServer.tables import User, EducationalOrganizations, TypeUser, TypeOrganizations
from MainServer.async_database import async_session
from MainServer.Models.EducationalOrganizations import TypeOrganization
from asyncio import run
from uuid import uuid4


async def create_model():
    async with async_session() as session:
        types_user = [
            TypeUser(
                name="admin",
                description="admin"
            ),
            TypeUser(
                name="user",
                description="user"
            )
        ]

        type_organization = [
            TypeOrganizations(
                name="Школа",
                start_range=1,
                end_range=11,
                description="Школа",
                postfix="класс"
            ),
            TypeOrganizations(
                name="Коледж",
                start_range=1,
                end_range=4,
                description="Коледж",
                postfix="курс"
            ),
            TypeOrganizations(
                name="Вуз",
                start_range=1,
                end_range=4,
                description="Вуз",
                postfix="курс"
            ),
        ]

        organization = [
            EducationalOrganizations(
                uuid=uuid4(),
                name_organizations="Астраханский технический лицей",
                type_organizations_id=1
            ),
            EducationalOrganizations(
                uuid=uuid4(),
                name_organizations="Астраханский государственный унивирситет им. Татищева",
                type_organizations_id=3
            )
        ]

        user = User(
            login="admin",
            id_type=1,
            id_edu_organization=1,
            stage_edu="1",
            name="Владислав",
            sename="Скрипник",
            secondname="Викторович"
        )
        user.password = "admin"
        session.add_all(types_user)
        session.add(user)
        session.add_all(type_organization)
        session.add_all(organization)

        await session.commit()


async def main():
    await create_model()


run(main())