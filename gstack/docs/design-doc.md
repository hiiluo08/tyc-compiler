# TyC Web Compiler (GStack) — Design Doc

## 1. Mục tiêu sản phẩm
- Public web compiler cho TyC.
- User có thể nhập source, stdin, bấm Run và nhận:
  - `stdout` khi chạy thành công.
  - `syntax_error`, `semantic_error`, `runtime_error`, `timeout`, `internal_error` theo status contract.
- User có thể xem AST ở cả `astText` và `astJson`.

## 2. User value
- Student/demo user có vòng lặp cực nhanh: viết code -> chạy -> xem lỗi theo stage.
- AST panel giúp học parser/AST mapping trực quan.
- UI giữ trạng thái rõ ràng (`idle`, `running`, `success`, `error`, `timeout`, `api_offline`).

## 3. Rủi ro chính
- Public code execution là rủi ro lớn nhất.
- Nếu không giới hạn tài nguyên và không isolate workspace theo request thì runner dễ bị treo, leak file, hoặc trả output không kiểm soát.

## 4. Quyết định kiến trúc
- Frontend: React + Vite + TypeScript trong `gstack/frontend/`, deploy Vercel.
- Backend runner: FastAPI trong `gstack/runner/`, chạy trên host Docker riêng.
- Compile/run pipeline trong runner:
  - Parse -> AST -> Semantic -> Codegen -> Assemble -> Run.
- Codegen không ghi vào root `src/runtime`; chỉ ghi vào temp dir theo request.

## 5. Alternatives đã cân nhắc
- A. Vercel-only runner: loại vì không phù hợp subprocess JVM + sandbox.
- B. Frontend Vercel + runner Docker (chọn): phù hợp đầy đủ scope compile/run thực tế.
- C. AST-only webapp: đơn giản hơn nhưng không đạt yêu cầu run đầy đủ.

## 6. Phạm vi implementation
- Build mọi artifact bên trong `gstack/`.
- Tái sử dụng vendor compiler/runtime từ code hiện có bằng cách copy vào `gstack/runner/`.
- Bổ sung guardrails: timeout, size limit, output truncation, CORS allowlist, cleanup, concurrency limit.

## 7. Done definition
- Runner có `/health`, `/api/v1/run`, `/api/v1/ast` theo contract.
- Frontend build pass và render đúng 3 tab Output/Errors/AST.
- Tests cover success, syntax error, semantic error (giữ AST), stdin, timeout, AST endpoint.
- Có security review, QA report, deployment notes, retro trong `gstack/docs/`.
- Không có file thay đổi ngoài `gstack/` cho phần công việc mới.