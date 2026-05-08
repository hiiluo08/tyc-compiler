# Proposal: tyc-web-compiler

## Intent
Đưa TyC compiler lên web public theo biến thể OpenSpec/OPSX, với frontend React + Vite deploy trên Vercel và runner backend tách riêng để compile/run an toàn.

## Why now
- Cần một bản web compiler public để demo và kiểm thử trải nghiệm end-to-end cho TyC.
- Cần đánh giá artifact-guided workflow (proposal/spec/design/tasks/apply/verify/archive) trên một bài toán brownfield thực tế.

## Scope

### In scope
- Frontend `openspec/frontend/` dùng React + Vite + TypeScript.
- Runner API `openspec/runner/` để parse, AST, semantic check, codegen, assemble, run.
- Trả diagnostics có cấu trúc cho syntax/semantic/runtime/timeout/internal errors.
- Hỗ trợ `stdin` cho `readInt/readFloat/readString`.
- Trả `stdout` khi chạy thành công.
- Trả AST cả text (`astText`) và JSON (`astJson`) cho source parse được.
- Public safety limits: kích thước input/output, timeout, CORS allowlist, cleanup workspace.
- Test và tài liệu deploy/verify trong `openspec/`.

### Out of scope
- Sửa root compiler (`src/`, `tests/`, `build/`, runtime root).
- Deploy production thực tế trong task này.
- Auth/account, persistent storage, share link, multi-file project.
- Arbitrary shell access/package install cho user.

## Product/architecture decisions
- Vercel chỉ host frontend.
- Runner chạy trên external Docker-capable host để hỗ trợ Python + JVM + Jasmin.
- Mỗi request dùng temp workspace riêng, cleanup trong `finally`.
- Vendor/copy/adapt compiler/runtime assets vào `openspec/runner/` để giữ isolation và tránh ghi vào root compiler runtime.

## Risks
1. **Public code execution risk**
   - Giảm thiểu: timeout, size limits, shell=False, non-root container, workspace per request.
2. **Runtime pollution ra ngoài openspec/**
   - Giảm thiểu: codegen output bắt buộc trỏ vào temp dir trong runner.
3. **Resource abuse (CPU/memory/output flood)**
   - Giảm thiểu: timeout cứng, output truncation, concurrency limit config.
4. **Divergence giữa vendor code và root compiler**
   - Giảm thiểu: giữ vendor copy tối thiểu + ghi rõ strategy cập nhật trong design/retrospective.

## Acceptance intent
Khi hoàn tất, mọi artifact và implementation phải nằm trong `openspec/`, đáp ứng contract ở `openspec/WEBAPP_SPEC.md`, verify pass và archive theo OpenSpec convention.