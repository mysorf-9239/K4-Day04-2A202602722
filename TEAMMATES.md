# Thành viên nhóm — Lab Day 04: IT Helpdesk Agent

## Danh sách và phân công

Phân công A–E theo lựa chọn của nhóm, sử dụng vai trò của phương án nhóm
5 người trong slide. Phân vai này không tự chỉ định trưởng nhóm.

| Vai trò | Họ và tên          | MSSV        | GitHub username                                       | Phần việc theo slide  | Công việc phụ trách                                                                                                 |
|---------|--------------------|-------------|-------------------------------------------------------|-----------------------|---------------------------------------------------------------------------------------------------------------------|
| A       | Nguyễn Đức Danh    | 2A202602722 | [mysorf-9239](https://github.com/mysorf-9239)         | Prompt                | Quản lý system_prompt.md, format JSON, context carry-over, kiểm tra nguồn ID và version evidence.                   |
| B       | Trần Đại Nhân      | 2A202602642 | [hugebenevolence](https://github.com/hugebenevolence) | Tool Schema           | Quản lý tools.yaml, chuẩn hóa enums/arguments, đồng bộ tool name và cấu hình Tavily API.                            |
| C       | Bùi Gia Chính      | 2A202602693 | [inosukeke](https://github.com/inosukeke)             | Eval Author — G01–G10 | Tự viết 10 case trong eval_group.json (5 single-turn + 5 multi-turn); chạy và phân tích group eval.                 |
| D       | Nguyễn Tú Tài      | 2A202602455 | [LonelyStar05](https://github.com/LonelyStar05)       | UI & Report Lead      | Dựng Live Chat Streamlit, thu transcript/ảnh demo và tổng hợp REPORT.md.                                            |
| E       | Lê Phan Việt Cường | 2A202602641 | [cuonglpv](https://github.com/cuonglpv)               | Security & Bonus Tool | Rà soát data leakage, ticket ngoài ý muốn, 12 adversarial case và phân tích sâu ít nhất 3 case; bonus tool nếu làm. |

## Cách phối hợp

1. Cả nhóm sử dụng một repository chung. Mỗi thành viên kiểm tra Git identity,
   tạo branch riêng, commit phần việc của mình rồi gửi pull request.
2. Cả nhóm giữ nguyên starter artifacts khi chạy baseline `v0`; phân tích trace
   của các nhóm lỗi thực tế quan sát được, không tạo evidence giả.
3. A và B phối hợp cải tiến tuần tự `v1 → v2 → v3`, thống nhất hypothesis,
   chạy lại base suite, kiểm tra regression và cập nhật `version_log.csv`.
4. C phát triển team eval; D phát triển UI và report; E kiểm thử an toàn.
   Kiểm chứng cuối cùng trên cùng phiên bản đã tích hợp của nhóm.
5. B phối hợp E chạy extension suite, kiểm tra external search và action boundary.
6. D tổng hợp report từ evidence do từng người cung cấp. Mỗi thành viên tự viết
   reflection của mình. UI dùng lại `run_model_tool_loop` trong `chat.py`, khai
   báo dependency Streamlit và hiển thị tool calls, args, result/error, version.
7. Run dùng làm evidence phải có `provider_error_cases == 0` và
   `measured_cases == total_cases`; vẫn phải review tool result/error thủ công.

## Trách nhiệm chung của từng thành viên

- Có đóng góp thực tế và ít nhất một commit bằng Git identity của mình xuất hiện
  trong lịch sử branch cuối cùng dùng để nộp.
- Tự viết và tự commit reflection cá nhân ở các mục B7.1–B7.5 trong
  `starter_v0/artifacts/REPORT.md` theo VLearn, gồm nhiệm vụ, failure mode đã
  trực tiếp phân tích và bài học. Giữ phần C2 của template repo và dẫn link đến
  reflection tương ứng; bổ sung các nội dung C2 yêu cầu, cùng file, commit hoặc
  PR có thật của mình.
  Không dùng riêng reflection làm bằng chứng duy nhất cho đóng góp kỹ thuật.
- Cùng thảo luận và hoàn thành reflection chung ở phần C1 của report.
- Không commit `.env`, API key, token, `.venv`, cache, generated tickets hoặc
  dữ liệu thật.
- Tự nộp cùng URL repository chung trên tài khoản VLearn của mình và kiểm tra
  URL đã được lưu chính xác.

## Evidence đóng góp cá nhân

Chỉ điền hash/PR thực tế sau khi đóng góp đã được merge vào branch nộp bài.
Các ô “Chưa cập nhật” không phải xác nhận đã hoàn thành công việc.

| Thành viên         | Commit hash / PR đóng góp                   | File / artifact liên quan                                                            |
|--------------------|---------------------------------------------|--------------------------------------------------------------------------------------|
| Nguyễn Đức Danh    | `3d89875`, `0601d08` (author danhnd)        | system_prompt.md, base runs, version_log.csv                                         |
| Trần Đại Nhân      | `c09b182` (author hugebenevolence)          | tools.yaml, v2 base run                                                              |
| Bùi Gia Chính      | `5344fd5` (author HocThoiJCang)             | eval_group.json, hai run v4;                                                         |
| Nguyễn Tú Tài      | `e8364fb` (author ColdDern)                 | app.py, UI_README.md, requirements.txt                                               |
| Lê Phan Việt Cường | `7f08d14` (lpvc), merge PR #1 tại `7d3a6d0` | search_device_info/tool.py, smoke_security_bonus.py, lookup_ticket_status và fixture |

## Checklist của trưởng nhóm trước khi nộp

- [x] Nhóm đã thống nhất phân công và mọi thành viên truy cập được repo chung.
- [x] Prompt, tool declarations và version log đủ `v0`, `v1`, `v2`, `v3`.
- [x] Có base runs cho `v0–v3`, 10 case nhóm, group run, extension run và
  adversarial evidence; đã rà soát đủ 12 security case.
- [x] Có Streamlit UI hoạt động, ảnh minh chứng, transcript và report hoàn chỉnh.
- [x] Reflection chung và self-reflection của cả 5 thành viên đã hoàn thành.
- [x] Commit của cả 5 thành viên đã có trên branch nộp bài; cách merge giữ được
  bằng chứng đóng góp cá nhân; bảng evidence ở trên đã có hash/PR thật.
- [x] Repository không chứa secret, dữ liệu thật hoặc file không được nộp.
- [x] Cả 5 thành viên đã nhận cùng URL repo và tự nộp trên VLearn.
