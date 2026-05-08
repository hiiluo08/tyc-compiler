# DevEx Review

## Developer workflow
- Runner test bằng `pytest` trong phạm vi `gstack/`.
- Frontend build/test bằng npm scripts trong `gstack/frontend/`.
- Không phụ thuộc root build output cho runtime execution.

## API ergonomics
- Contract response ổn định với fields cố định: `status`, `diagnostics`, `stages`, `astText`, `astJson`.
- Mapping lỗi theo stage giúp FE render trực tiếp.

## Local run expectations
- Frontend cần `VITE_TYC_API_BASE_URL` (prod bắt buộc).
- Runner dùng env limits để tune timeout/size/concurrency.

## Suggested improvements after v1
- Request ID + structured logs.
- Rate limit middleware.
- Optional queue mode cho burst traffic.