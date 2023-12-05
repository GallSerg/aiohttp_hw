import asyncio
import aiohttp


async def main():
    client = aiohttp.ClientSession()

    response = await client.post('http://127.0.0.1:8080/ads',
                                 json={"name": "first_ad",
                                       "title": "first ad is for apartment selling",
                                       "description": "first ad is for apartment selling - it's a very good flat"},
                                 )
    print(response.status)
    print(await response.json())

    response = await client.patch('http://127.0.0.1:8080/ads/7',
                                  json={"title": "first ad is for apartment tenancy"},
                                  )
    print(response.status)
    print(await response.json())

    response = await client.delete("http://127.0.0.1:8080/ads/7")
    print(response.status)
    print(await response.json())

    response = await client.get("http://127.0.0.1:8080/ads/7")
    print(response.status)
    print(await response.json())

    await client.close()


asyncio.run(main())
