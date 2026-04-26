import time

import httpx

from app.config import settings

_access_token = ""
_access_token_expire_at = 0.0


async def _fetch_access_token() -> str:
    global _access_token, _access_token_expire_at

    if not settings.wechat_appid or not settings.wechat_secret:
        return ""

    now = time.time()
    if _access_token and now < _access_token_expire_at:
        return _access_token

    token_url = "https://api.weixin.qq.com/cgi-bin/token"
    params = {
        "grant_type": "client_credential",
        "appid": settings.wechat_appid,
        "secret": settings.wechat_secret,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(token_url, params=params)
        response.raise_for_status()
        payload = response.json()

    token = str(payload.get("access_token", "")).strip()
    expires_in = int(payload.get("expires_in", 0) or 0)

    if not token or expires_in <= 0:
        return ""

    _access_token = token
    _access_token_expire_at = now + max(300, expires_in - 120)
    return _access_token


async def img_sec_check(image_url: str) -> bool:
    if not image_url:
        return True

    try:
        token = await _fetch_access_token()
        if not token:
            return True

        async with httpx.AsyncClient(timeout=15) as client:
            image_res = await client.get(image_url)
            image_res.raise_for_status()
            image_bytes = image_res.content

            check_url = f"https://api.weixin.qq.com/wxa/img_sec_check?access_token={token}"
            files = {"media": ("image.jpg", image_bytes, "image/jpeg")}
            check_res = await client.post(check_url, files=files)
            check_res.raise_for_status()
            check_payload = check_res.json()

        return int(check_payload.get("errcode", -1)) == 0
    except Exception:
        # 开发阶段失败放行，避免阻塞主流程
        return True
