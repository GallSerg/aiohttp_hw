import json
from aiohttp import web
from sqlalchemy.exc import IntegrityError

from models import Base, Session, Advertisment, engine

app = web.Application()


async def orm_context(app: web.Application):
    print("START")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    print("FINISH")


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response


app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)


def get_http_error(error_class, message):
    error = error_class(
        body=json.dumps({"error": message}), content_type="application/json"
    )
    return error


async def get_ad_by_id(session: Session, ad_id: int):
    ad = await session.get(Advertisment, ad_id)
    if ad is None:
        raise get_http_error(web.HTTPNotFound, f"Ad with id {ad_id} not found")
    return ad


async def add_ad(session: Session, ad: Advertisment):
    try:
        session.add(ad)
        await session.commit()
    except IntegrityError as error:
        raise get_http_error(web.HTTPConflict, "Ad already exists")
    return ad


class AdView(web.View):
    @property
    def ad_id(self):
        return int(self.request.match_info["ad_id"])

    @property
    def session(self) -> Session:
        return self.request.session

    async def get(self):
        ad = await get_ad_by_id(self.session, self.ad_id)
        return web.json_response(ad.dict)

    async def post(self):
        ad_data = await self.request.json()
        ad = Advertisment(**ad_data)
        ad = await add_ad(self.session, ad)
        return web.json_response({"id": ad.id})

    async def patch(self):
        ad = await get_ad_by_id(self.session, self.ad_id)
        ad_data = await self.request.json()
        for filed, value in ad_data.items():
            setattr(ad, filed, value)
        ad = await add_ad(self.session, ad)
        return web.json_response(ad.dict)

    async def delete(self):
        ad = await get_ad_by_id(self.session, self.ad_id)
        await self.session.delete(ad)
        await self.session.commit()
        return web.json_response({"status": "deleted"})


app.add_routes([web.post("/ads", AdView)])
app.add_routes([web.get("/ads/{ad_id:\d+}", AdView)])
app.add_routes([web.patch("/ads/{ad_id:\d+}", AdView)])
app.add_routes([web.delete("/ads/{ad_id:\d+}", AdView)])
web.run_app(app)
