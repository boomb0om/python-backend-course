import uvicorn
import json
import math
from urllib.parse import parse_qs


def fibonacci(n, memo={}):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    elif n in memo:
        return memo[n]
    else:
        memo[n] = fibonacci(n-1) + fibonacci(n-2)
        return memo[n]


async def parse_factorial(send, query_params) -> None:
    if 'n' not in query_params:
        return await http_response(send, 422, {"message": "Query parameter n is required"})
    
    try:
        n = int(query_params['n'][0])
    except Exception:
        return await http_response(send, 422, {"message": "Query parameter n must be an integer"})
    
    if n < 0:
        return await http_response(send, 400, {"message": "Query parameter n must be a positive integer"})
    
    result = math.factorial(n)
    await http_response(send, 200, {"result": result})


async def parse_fibbonachi(send, path) -> None:
    try:
        param = path.split('/fibonacci/')[-1]
        n = int(param)
    except ValueError:
        return await http_response(send, 422, {"message": "Path parameter n must be an integer"})
    
    if n < 0:
        return await http_response(send, 400, {"message": "Path parameter n must be a positive integer"})
    
    result = fibonacci(n)
    await http_response(send, 200, {"result": result})


async def parse_mean(send, body) -> None:
    try:
        data = json.loads(body)
    except Exception:
        return await http_response(send, 422, {"message": "Body must be an array of float or integers"})
    
    if not isinstance(data, list) or not all(isinstance(i, (int, float)) for i in data):
        return await http_response(send, 422, {"message": "Body must be an array of float or integers"})

    if not data:
        return await http_response(send, 400, {"message": "Array must not be empty"})

    result = sum(data) / len(data)
    await http_response(send, 200, {"result": result})


async def app(scope, receive, send) -> None:
    if scope["type"] != "http":
        return

    method = scope['method']
    path = scope['path']
    query_string = scope['query_string'].decode()
    query_params = parse_qs(query_string)

    if path == '/factorial' and method == 'GET':
        await parse_factorial(send, query_params)
    elif path.startswith('/fibonacci/') and method == 'GET':
        await parse_fibbonachi(send, path)
    elif path == '/mean' and method == 'GET':
        request = await receive()
        body = request['body'].decode('utf-8')
        await parse_mean(send, body)
    else:
        await http_response(send, 404, {"message": "Not Found"})


async def http_response(send, status, data) -> None:
    await send({
        'type': 'http.response.start',
        'status': status,
        'headers': [(b'content-type', b'application/json')],
    })
    await send({
        'type': 'http.response.body',
        'body': bytes(json.dumps(data), encoding="utf-8"),
    })


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, log_level="info")