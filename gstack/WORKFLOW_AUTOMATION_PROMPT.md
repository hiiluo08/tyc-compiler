# Prompt Tự Động Hóa GStack

Dán prompt này vào một phiên Claude Code mới để khởi động workflow GStack cho biến thể TyC Web Compiler trong folder `gstack/`.

```text
Bạn đang triển khai biến thể TyC Web Compiler theo workflow GStack.

Mục tiêu:
Xây dựng một web compiler public cho TyC, và chỉ làm việc trong folder gstack/. Frontend phải dùng React + Vite và có thể deploy lên Vercel. Backend runner phải expose API để compile/run code TyC, hiển thị syntax error, semantic error, runtime error, timeout error, trả stdout khi chạy thành công, và trả AST dạng text/JSON cho source parse được.

Spec có thẩm quyền:
- Đọc gstack/WEBAPP_SPEC.md trước và xem đó là product/spec contract cho biến thể workflow này.
- Nếu prompt này mâu thuẫn với gstack/WEBAPP_SPEC.md về hành vi sản phẩm, ưu tiên gstack/WEBAPP_SPEC.md.
- Nếu prompt này mâu thuẫn với isolation rules bên dưới, ưu tiên isolation rules.

Quy tắc isolation bắt buộc:
- Bạn chỉ được create, edit, delete, move, format, generate hoặc configure file bên trong gstack/.
- Bạn chỉ được read file bên ngoài gstack/ để hiểu compiler TyC hiện tại.
- Không modify src/, tests/, run.py, requirements.txt, CLAUDE.md, root specs, root package files, root Docker/Vercel config, root workflow artifacts, hoặc bất kỳ generated file nào bên ngoài gstack/.
- Không dùng Bash để ghi ngoài gstack/: không redirect output, không tạo folder/file, không chạy formatter/generator/package manager với output ngoài gstack/.
- Nếu một tool chỉ hỗ trợ repo-wide write hoặc không thể scope chắc chắn vào gstack/, không dùng tool đó.
- Nếu thấy cần thay đổi bất kỳ file nào ngoài gstack/, hãy dừng lại và hỏi user trước khi làm.
- Nếu một GStack command/agent đề xuất broad cleanup, repo-wide refactor, cross-folder edits, push, PR, deploy, hoặc commit ngoài scope, hãy từ chối phần đó trừ khi user approve rõ ràng.

Hướng dẫn dùng GStack:
- Dùng staged flow của GStack: Think -> Plan -> Build -> Review -> Test -> Ship -> Reflect.
- Khi một GStack slash command phù hợp, hãy invoke skill đó thay vì tự trả lời ad-hoc.
- Dùng /browse cho browser/web QA. Không dùng mcp__claude-in-chrome__* tools.
- GStack skills có thể auto-fix hoặc đề xuất commit. Chỉ chấp nhận fix nếu toàn bộ write nằm trong gstack/. Không push, create PR, merge, hoặc deploy trừ khi user yêu cầu rõ ràng.
- Lưu mọi workflow artifacts trong gstack/docs/. Nếu một skill mặc định muốn ghi nơi khác, hãy chuyển/summarize artifact về gstack/docs/ và không ghi ngoài gstack/.

Sequence đề xuất:
1. Safety/scope guard:
   - Chạy /guard hoặc /freeze và chọn path gstack/ để lock edits trong gstack/.
   - Nhớ rằng /freeze chỉ chặn Edit/Write; vẫn phải tự cấm Bash writes ngoài gstack/.
   - Nếu /guard hoặc /freeze không khả dụng, tự enforce isolation rules trước mọi tool call.
2. Think:
   - Chạy /office-hours để làm rõ problem, risks, user value, và alternatives.
   - Lưu/summarize kết quả vào gstack/docs/design-doc.md.
3. Plan:
   - Chạy /autoplan nếu có để lấy CEO/product, design, và engineering review.
   - Nếu /autoplan không cover developer experience cho API/runner/frontend workflow, chạy thêm /plan-devex-review.
   - Nếu cần tách thủ công, chạy /plan-ceo-review, /plan-eng-review, /plan-design-review, và /plan-devex-review.
   - Lưu artifacts chỉ dưới gstack/docs/:
     - design-doc.md
     - architecture-review.md
     - design-review.md
     - devex-review.md
4. Build:
   - Chỉ implement sau khi plan đã coherent và không vi phạm isolation.
   - Đặt frontend dưới gstack/frontend/.
   - Đặt runner dưới gstack/runner/.
   - Đặt tests dưới gstack/tests/.
   - Đặt docs/reports dưới gstack/docs/.
5. Review:
   - Chạy /review cho code review nếu có, nhưng chỉ apply fixes trong gstack/.
   - Chạy /cso hoặc security review tương đương cho rủi ro public code execution.
   - Lưu findings vào gstack/docs/security-review.md và chỉ fix files bên trong gstack/.
6. Test:
   - Chạy backend tests cho runner.
   - Chạy frontend build.
   - Dùng /browse cho browser/manual QA nếu có local URL hoặc deployed preview.
   - Dùng /qa hoặc /qa-only chỉ khi có thể scope fix/report vào gstack/; nếu không chắc, dùng /qa-only hoặc tự viết QA report.
   - Lưu QA results vào gstack/docs/qa-report.md.
7. Ship:
   - Không chạy /ship tự động vì /ship có thể push/create PR theo workflow GStack.
   - Thay vào đó, chuẩn bị Vercel frontend deployment notes và Docker runner deployment notes dưới gstack/docs/.
   - Nếu user yêu cầu rõ ràng việc push/PR/deploy, hỏi lại scope và credentials trước khi làm.
8. Reflect:
   - Chạy /retro nếu phù hợp hoặc tự viết retro.
   - Viết gstack/docs/retro.md để so sánh workflow GStack đã hoạt động thế nào cho task này.

Ràng buộc implementation:
- Không import và dùng root codegen theo cách có thể write vào root src/runtime/.
- Generate ANTLR/parser artifacts bên trong gstack/runner/build/ nếu cần.
- Copy runtime/compiler assets vào gstack/ chỉ khi cần modifications hoặc cần sandbox path ổn định.
- Toàn bộ webapp dependencies và lockfiles phải nằm trong gstack/frontend/ hoặc gstack/runner/.
- Runner phải dùng per-request temp directories, timeouts, output truncation, CORS allowlist, cleanup, và không execute untrusted code ngoài sandbox/temp dir.
- Không log secrets, tokens, full env, hoặc unbounded stdout/stderr.

Yêu cầu verification:
- Backend tests cho success, syntax error, semantic error, AST endpoint, stdin, và timeout.
- Frontend build pass.
- Browser/manual QA plan hoặc /browse evidence tồn tại.
- Security review cho public code execution tồn tại.
- Không có changed repo files ngoài gstack/.
- Final report phải gồm design/review/security/QA/retro docs được tạo bởi GStack process.

Hãy chạy tự động qua workflow nhiều nhất có thể, nhưng dừng ngay nếu isolation rule bị vi phạm, nếu một workflow tool không thể scope vào gstack/, hoặc nếu cần quyết định thật về deployment credential/domain.
```
