# Prompt Tự Động Hóa OpenSpec

Dán prompt này vào một phiên Claude Code mới để khởi động workflow OpenSpec/OPSX cho biến thể TyC Web Compiler trong folder `openspec/`.

```text
Bạn đang triển khai biến thể TyC Web Compiler theo workflow OpenSpec hiện đại, tức OPSX artifact-guided workflow.

Tinh thần OpenSpec cần tuân thủ:
- Fluid, not rigid: workflow là các action có thể lặp lại, không phải phase gate cứng.
- Iterative, not waterfall: khi implementation phát hiện design/spec sai, cập nhật artifact tương ứng rồi tiếp tục.
- Brownfield-first: repo đã có compiler TyC; chỉ đọc compiler hiện tại để hiểu pipeline, không sửa root compiler.
- Agree before build: phải có proposal/specs/design/tasks đủ rõ trước khi implement.

Mục tiêu:
Xây dựng một web compiler public cho TyC, và chỉ làm việc trong folder openspec/. Frontend phải dùng React + Vite và có thể deploy lên Vercel. Backend runner phải expose API để compile/run code TyC, hiển thị syntax error, semantic error, runtime error, timeout error, trả stdout khi chạy thành công, và trả AST dạng text/JSON cho source parse được.

Spec có thẩm quyền:
Đọc openspec/WEBAPP_SPEC.md trước và xem đó là product/spec contract cho biến thể workflow này. Mọi proposal, delta spec, design, tasks, apply, verify, archive, và retrospective đều phải trace về file này.

Environment preflight nếu repo yêu cầu:
- Nếu CLAUDE.md của repo yêu cầu kiểm tra gstack trước mọi AI-assisted work, chỉ thực hiện bước kiểm tra bắt buộc đó như environment preflight.
- Bước này không thuộc workflow OpenSpec và không được tính là GStack workflow.
- Không dùng GStack staged flow, GStack review/QA/ship skills, hoặc GStack artifacts cho biến thể OpenSpec trừ khi user yêu cầu rõ ràng.
- Sau preflight, tiếp tục theo OpenSpec/OPSX workflow và chỉ tạo/sửa artifacts trong openspec/.

Quy tắc isolation bắt buộc:
- Bạn chỉ được create, edit, delete, move, format, generate hoặc configure file bên trong openspec/.
- Bạn chỉ được read file bên ngoài openspec/ để hiểu compiler TyC hiện tại.
- Không modify src/, tests/, run.py, requirements.txt, CLAUDE.md, root specs, root package files, root Docker/Vercel config, root .claude/, root OpenSpec artifacts, hoặc bất kỳ generated file nào bên ngoài openspec/.
- Nếu thấy cần thay đổi bất kỳ file nào ngoài openspec/, hãy dừng lại và hỏi user trước khi làm.
- Nếu OpenSpec CLI/slash command muốn chạy `openspec init` hoặc `openspec update` và có thể write ra `.claude/`, root config, hoặc artifact ngoài openspec/, không chạy command đó. Hãy tạo artifact tương đương thủ công trong openspec/.
- Nếu một tool không thể scope vào openspec/, không chạy tool đó. Thay vào đó tạo artifact tương đương theo đúng OpenSpec/OPSX structure bên trong openspec/.

OpenSpec/OPSX model cần áp dụng:
- Default core profile: /opsx:propose -> /opsx:apply -> /opsx:sync -> /opsx:archive.
- Expanded workflow nếu có sẵn: /opsx:explore, /opsx:new, /opsx:continue, /opsx:ff, /opsx:apply, /opsx:verify, /opsx:sync, /opsx:archive, /opsx:bulk-archive.
- Artifact mặc định của schema `spec-driven`:
  - proposal.md: why/what, intent, scope, high-level approach.
  - specs/: delta specs với ADDED/MODIFIED/REMOVED Requirements và Scenarios.
  - design.md: technical approach, architecture decisions, data/API flow, file layout.
  - tasks.md: implementation checklist với checkbox.
- Main specs là source of truth dưới openspec/specs/.
- Active change nằm dưới openspec/changes/<change-name>/.
- Khi archive, completed change phải nằm dưới openspec/changes/archive/YYYY-MM-DD-<change-name>/ theo convention của OpenSpec.

Tên change bắt buộc:
Dùng change name `tyc-web-compiler` trừ khi user yêu cầu khác.

## 0. Safety/context setup

Trước khi tạo hoặc sửa artifact:
1. Đọc openspec/WEBAPP_SPEC.md.
2. Read-only inspect compiler root nếu cần để hiểu pipeline: grammar -> parser -> ASTGeneration -> StaticChecker -> CodeGenerator -> Jasmin/JVM runtime.
3. Kiểm tra mọi planned write đều nằm dưới openspec/.
4. Không chạy command cài đặt, init, update, hoặc generator nào nếu nó có thể write ngoài openspec/.

Nếu OpenSpec đã được init và /opsx commands hoạt động trong scope an toàn, dùng commands. Nếu không, tạo thủ công các artifact tương đương.

## 1. Explore khi requirements còn mơ hồ

Nếu còn gray area lớn, dùng:

/opsx:explore TyC Web Compiler in openspec/ with strict isolation

Mục tiêu explore:
- Làm rõ public runner risk, Vercel frontend/external Docker runner split, AST display, diagnostics, stdin, timeout.
- Không tạo artifact nếu chưa cần.
- Nếu /opsx:explore không available, ghi exploration notes ngắn trong openspec/changes/tyc-web-compiler/exploration.md.

Không dùng explore để thay thế proposal/spec/design/tasks. Explore chỉ giúp làm rõ trước khi propose.

## 2. Propose change

Ưu tiên default core path:

/opsx:propose tyc-web-compiler

Nếu command không available hoặc không scope được vào openspec/, tạo thủ công:

openspec/changes/tyc-web-compiler/proposal.md

Proposal phải gồm:
- Intent: đưa TyC compiler lên web public.
- Scope in/out:
  - In: React + Vite frontend, runner API, compile/run, diagnostics, AST, stdin, timeout, docs/deploy notes, tests.
  - Out: sửa root compiler, deploy thật, auth/user accounts, persistent storage, online package install, arbitrary shell access.
- Approach:
  - Vercel chỉ host frontend.
  - External Docker runner xử lý Python/JVM/Jasmin execution.
  - Runner dùng per-request temp workspace và cleanup.
  - Vendor/copy/adapt compiler/runtime assets trong openspec/ khi cần để tránh write ra root.
- Risks:
  - Public code execution.
  - Root runtime pollution.
  - Timeout/resource abuse.
  - Divergence giữa vendor code và root compiler.

## 3. Create delta specs

Nếu dùng expanded workflow, sau /opsx:new có thể dùng /opsx:continue hoặc /opsx:ff. Nếu dùng core profile, /opsx:propose thường đã tạo specs.

Artifacts spec tối thiểu phải nằm tại:

openspec/changes/tyc-web-compiler/specs/web-compiler/spec.md

Nếu OpenSpec generated path khác nhưng vẫn dưới openspec/changes/tyc-web-compiler/specs/, giữ path đó nếu hợp lý.

Delta spec phải dùng OpenSpec format:

## ADDED Requirements

Bắt buộc có requirements/scenarios cho:
- Source editing and sample programs.
- Compile/run success returning stdout.
- Syntax error diagnostics.
- Semantic error diagnostics.
- Runtime error diagnostics.
- Timeout diagnostics.
- AST text/JSON display for parseable source.
- Stdin support for readInt/readFloat/readString.
- Output truncation.
- Runner health/API contract.
- Isolation: no writes outside openspec/.
- Deployment notes: Vercel frontend + external Docker runner.

Scenario nên dùng Given/When/Then hoặc cấu trúc tương đương, đủ testable.

Không đưa chi tiết implementation quá sâu vào spec; chi tiết technical để trong design.md và tasks.md.

## 4. Create design

Nếu /opsx:continue hoặc /opsx:ff available, dùng chúng để tạo design. Nếu không, tạo thủ công:

openspec/changes/tyc-web-compiler/design.md

Design phải gồm:
- Architecture overview:
  - openspec/frontend/: React + Vite app.
  - openspec/runner/: backend API/runner.
  - openspec/tests/ hoặc test folders tương ứng bên trong frontend/runner/.
  - openspec/docs/: deployment, QA, retrospective nếu cần.
- API design:
  - GET /health.
  - POST /api/v1/run.
  - POST /api/v1/ast.
  - Response contract gồm ok/status/stdout/stderr/diagnostics/astText/astJson/stages/durationMs/truncated.
- Diagnostics model:
  - syntax_error, semantic_error, runtime_error, timeout, internal_error.
  - message, stage, line/column nếu có, raw output nếu an toàn.
- Compiler integration strategy:
  - Root compiler chỉ read-only.
  - Không dùng root codegen nếu nó write vào src/runtime/.
  - Generate ANTLR/parser artifacts trong openspec/runner/build/ nếu cần.
  - Copy/adapt runtime/compiler assets vào openspec/runner/ khi cần.
  - Per-request temp workspace cho generated .tyc/.j/.class files.
- AST serialization:
  - astText = str(ast).
  - astJson recursively serialize node kind + fields.
- Security/runtime policy:
  - subprocess shell=False.
  - timeoutSeconds budget chung cho compile+assemble+run ở bản đầu.
  - source/stdin/output size limits.
  - CORS allowlist.
  - non-root Docker user.
  - cleanup trong finally.
- Deployment design:
  - Vercel frontend env var trỏ tới runner URL.
  - Runner deploy bằng Docker trên platform hỗ trợ long-running process/JVM.
- Isolation verification:
  - Cách chứng minh không file ngoài openspec/ bị generate/modify.

## 5. Create tasks

Nếu /opsx:continue hoặc /opsx:ff available, dùng chúng để tạo tasks. Nếu không, tạo thủ công:

openspec/changes/tyc-web-compiler/tasks.md

Tasks phải có checkbox OpenSpec-style và chia thành nhóm nhỏ:
- Project scaffolding trong openspec/.
- Runner API foundation.
- Compiler integration/vendor/runtime assets.
- AST serializer.
- Diagnostics and response contract.
- Workspace/timeout/cleanup policy.
- Frontend React + Vite editor/output/errors/AST tabs/samples.
- Deployment docs/config.
- Tests and verification.
- Archive/retro notes.

Mỗi task phải đủ nhỏ để /opsx:apply hoặc agent implementation có thể hoàn thành và check off được.

## 6. Apply implementation

Khi proposal/specs/design/tasks đã đủ rõ, chạy:

/opsx:apply tyc-web-compiler

Nếu /opsx:apply không available hoặc không thể scope vào openspec/, implement thủ công theo openspec/changes/tyc-web-compiler/tasks.md.

Trong apply:
- Chỉ sửa files dưới openspec/.
- Đánh dấu task hoàn thành bằng checkbox [x] ngay khi xong.
- Nếu implementation phát hiện spec/design sai, cập nhật artifact tương ứng rồi tiếp tục. Đây là đúng tinh thần OPSX.
- Không push, create PR, deploy thật, hoặc commit nếu user chưa yêu cầu.

Implementation constraints bắt buộc:
- Không import và dùng root codegen theo cách có thể write vào root src/runtime/.
- Generate ANTLR/parser artifacts bên trong openspec/runner/build/ nếu cần.
- Copy runtime/compiler assets vào openspec/ chỉ khi cần để runner tự chủ hoặc để sửa path/output behavior.
- Toàn bộ webapp dependencies và lockfiles phải nằm trong openspec/frontend/ hoặc openspec/runner/.
- Runner phải dùng per-request temp directories, timeout, output truncation, CORS allowlist, và cleanup.

## 7. Verify implementation

Nếu expanded command available, chạy:

/opsx:verify tyc-web-compiler

Nếu không, verify thủ công và lưu report tại:

openspec/changes/tyc-web-compiler/verification.md

Verification phải kiểm tra 3 dimension theo OpenSpec:
- Completeness: tasks đã check, requirements/scenarios có implementation/test tương ứng.
- Correctness: behavior khớp spec intent và API contract.
- Coherence: design decisions phản ánh trong code, không drift hoặc nếu drift thì design đã được update.

Verification tối thiểu:
- Backend tests cho success, syntax error, semantic error, runtime error, AST endpoint, stdin, và timeout.
- Frontend build pass.
- API responses khớp contract trong openspec/WEBAPP_SPEC.md và delta specs.
- Không có changed/generated files bên ngoài openspec/.
- Không có .j/.class/runtime artifacts rò ra root src/runtime/ hoặc root build/.
- Manual QA plan cho UI editor/output/errors/AST tabs/samples.

Nếu verify fail:
1. Ghi rõ failure trong verification.md.
2. Update tasks.md với fix tasks còn thiếu.
3. Update spec/design nếu artifact đã sai so với implementation đúng.
4. Chạy lại apply/fix.
5. Chạy lại verify.

## 8. Sync specs

Sau khi verify pass, dùng core command nếu available:

/opsx:sync tyc-web-compiler

Mục tiêu:
- Merge delta specs từ openspec/changes/tyc-web-compiler/specs/ vào openspec/specs/.
- Giữ openspec/specs/ là source of truth sau khi change hoàn thành.

Nếu /opsx:sync không available, merge thủ công delta specs vào openspec/specs/web-compiler/spec.md theo đúng semantics:
- ADDED Requirements: append vào main spec.
- MODIFIED Requirements: replace requirement tương ứng.
- REMOVED Requirements: remove requirement tương ứng.

Không sync vào bất kỳ root spec folder nào ngoài openspec/.

## 9. Archive and reflect

Sau sync/verify, chạy:

/opsx:archive tyc-web-compiler

Archive đúng convention OpenSpec:

openspec/changes/archive/YYYY-MM-DD-tyc-web-compiler/

Nếu /opsx:archive không available hoặc không scope được, archive thủ công bằng cách move folder active change vào path trên, chỉ bên trong openspec/changes/archive/.

Trước khi archive hoặc trong archive folder, tạo retrospective nếu chưa có:

openspec/changes/tyc-web-compiler/retrospective.md

hoặc sau khi archive:

openspec/changes/archive/YYYY-MM-DD-tyc-web-compiler/retrospective.md

Retrospective phải đánh giá:
- OpenSpec/OPSX giúp rõ intent/scope/spec/design/tasks thế nào.
- Điểm mạnh/yếu khi dùng delta specs cho web compiler brownfield.
- Friction do isolation rule hoặc tooling không scope được.
- Bài học để so sánh với GSD và GStack.

## 10. Final report

Khi hoàn tất, báo cáo ngắn gọn:
- Commands OpenSpec/OPSX đã dùng, hoặc fallback thủ công nào đã dùng.
- Artifacts đã tạo/cập nhật:
  - openspec/specs/...
  - openspec/changes/tyc-web-compiler/...
  - openspec/changes/archive/YYYY-MM-DD-tyc-web-compiler/...
- Implementation summary: frontend, runner, AST, diagnostics, deployment docs.
- Verification results: backend tests, frontend build, isolation check, manual QA plan.
- Archive location.
- Workflow evaluation: hiệu quả, friction, bài học so sánh với GSD/GStack.
- Xác nhận không sửa file ngoài openspec/.

Nguyên tắc vận hành cuối cùng:
- Ưu tiên OPSX core path nếu commands hoạt động an toàn: /opsx:propose -> /opsx:apply -> /opsx:sync -> /opsx:archive.
- Dùng expanded commands khi có lợi: /opsx:explore cho unclear requirements, /opsx:new + /opsx:continue cho step-by-step control, /opsx:ff khi scope rõ, /opsx:verify trước archive.
- Không coi workflow là waterfall cứng; update proposal/spec/design/tasks khi học được điều mới.
- Nhưng không implement trước khi có artifacts đủ rõ.
- Luôn dừng và hỏi user nếu cần deployment credential/domain, nếu tool muốn write ngoài openspec/, hoặc nếu isolation rule có nguy cơ bị phá vỡ.
```
