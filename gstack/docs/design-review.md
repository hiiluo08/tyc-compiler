# Design Review (UI/UX)

## Layout contract
- Header + toolbar (Run, Load Sample, Clear).
- 2-column: Code Editor | Result Panel.
- Stdin panel ở dưới.

## UX expectations
- Run bị disable khi `running`, luôn re-enable khi xong hoặc timeout.
- Errors tab hiển thị status + stages + diagnostics + stderr.
- AST tab hỗ trợ tree view và text fallback.
- Offline API có thông báo thân thiện, không crash UI.

## Visual quality checks
- Editor tối thiểu 400px, tabSize=4, monospace.
- Mobile fallback: layout chuyển 1 cột ở màn hình hẹp.
- Trạng thái màu/nhãn rõ cho success/error/timeout.