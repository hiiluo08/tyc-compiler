# Prompt Tự Động Hóa GSD

Dán prompt này vào một phiên Claude Code mới để khởi động workflow GSD cho biến thể TyC Web Compiler trong folder `gsd/`.

```text
Bạn đang triển khai biến thể TyC Web Compiler theo workflow GSD, và phải áp dụng đúng vòng lặp 6 command của get-shit-done:

1. Initialize
2. Discuss
3. Plan
4. Execute
5. Verify
6. Repeat -> Ship

Mục tiêu:
Xây dựng một web compiler public cho TyC, và chỉ làm việc trong folder gsd/. Frontend phải dùng React + Vite và có thể deploy lên Vercel. Backend runner phải expose API để compile/run code TyC, hiển thị syntax error, semantic error, runtime error, timeout error, trả stdout khi chạy thành công, và trả AST dạng text/JSON cho source parse được.

Spec có thẩm quyền:
Đọc gsd/WEBAPP_SPEC.md trước và xem đó là product/spec contract cho biến thể workflow này. Mọi requirements, phase, task, và verification đều phải trace về spec này.

Quy tắc isolation bắt buộc:
- Bạn chỉ được create, edit, delete, move, format, generate hoặc configure file bên trong gsd/.
- Bạn chỉ được read file bên ngoài gsd/ để hiểu compiler TyC hiện tại.
- Không modify src/, tests/, run.py, requirements.txt, CLAUDE.md, root specs, root package files, root Docker/Vercel config, root .planning/, hoặc bất kỳ generated file nào bên ngoài gsd/.
- Nếu thấy cần thay đổi bất kỳ file nào ngoài gsd/, hãy dừng lại và hỏi user trước khi làm.
- Nếu một GSD command muốn tạo .planning/ ở repo root, hãy dừng lại và reconfigure sang gsd/.planning/ hoặc hỏi user.
- Nếu một GSD command không thể scope vào gsd/, không chạy command đó. Thay vào đó hãy tạo artifact tương đương theo phong cách GSD bên trong gsd/.planning/.

Cách áp dụng vòng lặp GSD cho project này:

## 1. Initialize

Vì repo đã có code compiler TyC, hãy bắt đầu bằng:

/gsd-map-codebase

Mục tiêu của bước này:
- Analyze stack, architecture, conventions của compiler TyC hiện tại ở chế độ read-only.
- Tập trung vào pipeline: grammar -> parser -> ASTGeneration -> StaticChecker -> CodeGenerator -> Jasmin/JVM runtime.
- Output artifacts chỉ được nằm trong gsd/.planning/ hoặc gsd/docs/.
- Không edit compiler root.

Sau đó chạy:

/gsd-new-project

Mục tiêu của bước này:
- Tạo project context cho biến thể gsd web compiler.
- Tạo requirements và roadmap dựa trên gsd/WEBAPP_SPEC.md.
- Roadmap phải chia thành các phase build được, không chỉ mô tả chung chung.
- Nếu GSD yêu cầu user approve roadmap, hãy trình bày summary ngắn gọn và chờ approval trước khi build.

Roadmap tối thiểu nên có các phase sau:
1. Runner backend foundation và API schemas.
2. Isolated compiler integration, ANTLR/build/runtime assets, temp workspace.
3. AST serialization và diagnostics contract.
4. React + Vite frontend, editor, output/errors/AST tabs, samples.
5. Deployment docs/config cho Vercel frontend và Docker runner.
6. Tests, verification, hardening, và retrospective.

## 2. Discuss

Với từng phase N trong roadmap, chạy:

/gsd-discuss-phase N

Mục tiêu của discuss:
- Chuyển mô tả phase ngắn trong roadmap thành decisions đủ rõ để build.
- Capture các gray areas trước khi planning.
- Với project này, discuss phải làm rõ ít nhất:
  - file layout bên trong gsd/ cho phase đó
  - API shape nếu phase liên quan backend
  - error handling và diagnostics nếu phase liên quan runner
  - data structures nếu phase liên quan AST/response schema
  - UI layout nếu phase liên quan frontend
  - test cases và acceptance criteria
  - cách đảm bảo không write ra ngoài gsd/

Nếu user không trả lời thêm, dùng reasonable defaults từ gsd/WEBAPP_SPEC.md, nhưng vẫn ghi rõ assumptions trong artifact của phase.

## 3. Plan

Sau discuss cho phase N, chạy:

/gsd-plan-phase N

Mục tiêu của plan:
- Research -> plan -> verify trong vòng lặp cho đến khi plan pass.
- Mỗi plan phải đủ nhỏ để execute trong fresh context.
- Plan phải chỉ ra chính xác files bên trong gsd/ sẽ được create/edit.
- Plan phải có verification criteria rõ ràng.
- Plan không được chứa task sửa file ngoài gsd/.

Nếu plan đề xuất sửa root compiler, root requirements, root tests, hoặc root config, plan đó fail. Hãy replan bằng cách copy/adapt hoặc tạo wrapper bên trong gsd/.

## 4. Execute

Khi plan của phase N đã pass, chạy:

/gsd-execute-phase N

Mục tiêu của execute:
- Execute plan theo parallel waves nếu GSD hỗ trợ.
- Mỗi executor làm việc trong fresh context.
- Mỗi task nên có atomic commit nếu workflow đang được phép commit; nếu user chưa yêu cầu commit, không tự commit.
- Mọi implementation phải nằm trong gsd/.
- Không tạo generated files ngoài gsd/.

Trong project này, execute phải tuân thủ các ràng buộc implementation sau:
- Không import và dùng root codegen theo cách có thể write vào root src/runtime/.
- Generate ANTLR/parser artifacts bên trong gsd/runner/build/ nếu cần.
- Copy runtime/compiler assets vào gsd/ chỉ khi cần modifications.
- Toàn bộ webapp dependencies và lockfiles phải nằm trong gsd/frontend/ hoặc gsd/runner/.
- Runner phải dùng per-request temp directories, timeouts, output truncation, CORS allowlist, và cleanup.

## 5. Verify

Sau execute cho phase N, chạy:

/gsd-verify-work N

Mục tiêu của verify:
- Walk through thứ vừa build so với phase goal và gsd/WEBAPP_SPEC.md.
- Không chỉ kiểm tra task completed; phải kiểm tra feature có thực sự đạt yêu cầu không.
- Nếu broken, GSD phải tạo diagnosed fix plan.
- Không debug thủ công lan man trong main context. Sau khi có fix plan, chạy lại execute cho phase đó.

Verification tối thiểu toàn project:
- Backend tests cho success, syntax error, semantic error, AST endpoint, stdin, và timeout.
- Frontend build pass.
- Không có changed files bên ngoài gsd/.
- Không có generated .j/.class/runtime artifacts rò ra root src/runtime/ hoặc root build/.
- API responses khớp contract trong gsd/WEBAPP_SPEC.md.

Nếu verify fail:
1. Ghi rõ failure.
2. Tạo fix plan trong gsd/.planning/.
3. Chạy lại /gsd-execute-phase N cho fix plan.
4. Chạy lại /gsd-verify-work N.

## 6. Repeat -> Ship

Sau khi phase N verify pass, chạy:

/gsd-ship N

Mục tiêu của ship phase:
- Chuẩn bị phase để được coi là complete.
- Không push, create PR, hoặc deploy thật nếu user chưa yêu cầu.
- Ghi lại ship notes/artifacts bên trong gsd/.

Sau đó lặp lại:

/gsd-discuss-phase N+1
/gsd-plan-phase N+1
/gsd-execute-phase N+1
/gsd-verify-work N+1
/gsd-ship N+1

Tiếp tục cho đến khi toàn bộ milestone web compiler trong gsd/ hoàn thành.

Khi milestone hoàn thành, chạy:

/gsd-complete-milestone

Mục tiêu:
- Archive milestone artifacts bên trong gsd/.
- Ghi retrospective về việc dùng GSD workflow cho project này.
- So sánh điểm mạnh/yếu của GSD với mục tiêu vibecode webapp.

Chỉ chạy:

/gsd-new-milestone

nếu user muốn tiếp tục milestone mới sau bản web compiler đầu tiên.

Nguyên tắc vận hành:
- Không thay vòng lặp này bằng một lệnh autonomous chung nếu điều đó làm mất khả năng đánh giá từng bước của GSD.
- Luôn đi theo thứ tự: Initialize -> Discuss -> Plan -> Execute -> Verify -> Ship -> Repeat.
- Khi cần approval thật, hãy dừng và hỏi user.
- Khi có rủi ro vi phạm isolation rule, hãy dừng và hỏi user.

Final report khi hoàn tất:
- Liệt kê phases đã chạy.
- Liệt kê commands GSD đã dùng.
- Tóm tắt artifacts đã tạo trong gsd/.
- Tóm tắt tests/verification đã pass hoặc còn thiếu.
- Xác nhận không sửa file ngoài gsd/.
- Đánh giá workflow GSD: điểm hiệu quả, điểm gây friction, và bài học cho hai workflow còn lại.
```
