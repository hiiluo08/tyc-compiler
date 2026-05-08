# Architecture Review

## Recommended architecture
- `gstack/frontend/` (Vite SPA) gọi HTTPS API đến runner.
- `gstack/runner/` (FastAPI) xử lý pipeline compile/run và trả JSON contract.

## Key decisions
1. Isolated vendor compiler trong `gstack/runner/compiler_vendor/` để tránh write sang root.
2. Runtime workspace per-request trong `gstack/runner/tmp/` và cleanup ở `finally`.
3. Chuẩn hóa status/stage để frontend render nhất quán theo spec.

## Tradeoffs
- Ưu điểm: giữ isolation tuyệt đối, deploy linh hoạt, dễ harden bảo mật.
- Nhược điểm: thêm độ phức tạp vận hành vì tách frontend và runner.

## Risk mitigations
- Timeout cứng cho assemble/run.
- Limit source/stdin/output bytes.
- CORS allowlist theo env.
- Semaphore giới hạn concurrent runs.
- Không dùng `shell=True`, không dùng user-supplied filename.