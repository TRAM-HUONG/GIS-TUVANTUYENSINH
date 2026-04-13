import random
from django.urls import reverse

def get_ai_response(user_message):
    msg = user_message.lower()
    
    # 1. DANH SÁCH LỜI CHÀO
    greetings = [
        "Xin chào! Rất vui được gặp bạn. Mình có thể giúp gì cho bạn trong kỳ tuyển sinh này không?",
        "Chào bạn nhé! Chúc bạn một ngày tốt lành. Bạn cần tra cứu thông tin gì nè?",
        "Hi! Trợ lý ảo GIS-TVTS đã sẵn sàng. Bạn muốn tìm hiểu về trường hay ngành học thế nào?"
    ]

    # 2. XỬ LÝ CÂU CHÀO
    if any(word in msg for word in ["chào", "hi", "hello"]):
        return random.choice(greetings)

    # 3. TRƯỜNG ĐÀO TẠO -> Gửi thẻ <a> để nhấn được
    elif any(word in msg for word in ["trường", "đại học", "cơ sở", "đào tạo"]):
        try:
            url = reverse('truong_list')
            return (f"Dạ, về danh sách các trường đại học, bạn xem chi tiết tại đây giúp mình nhé: "
                    f"<a href='{url}' class='chat-link'>Danh sách trường Đại học</a>. "
                    "<br>Nếu bạn muốn tư vấn trường phù hợp với điểm số, hãy nhắn Zalo Admin nha!")
        except:
            return "Bạn có thể xem mục 'Trường' trên Menu nhé. Cần tư vấn sâu hãy nhắn Zalo cho mình!"

    # 4. NGÀNH HỌC PHÙ HỢP -> Gửi thẻ <a> để nhấn được
    elif any(word in msg for word in ["ngành", "phù hợp", "chọn ngành", "định hướng", "nên học gì"]):
        try:
            url = reverse('khao_sat')
            return (f"Chọn ngành là quyết định rất quan trọng nè! Bạn thử làm bài khảo sát định hướng tại đây: "
                    f"<a href='{url}' class='chat-link'>Làm bài khảo sát</a>. "
                    "<br>Có kết quả rồi hãy gửi qua Zalo để Admin tư vấn lộ trình học cho bạn!")
        except:
            return "Bạn hãy vào mục 'Khảo sát' để xem mình hợp với ngành nào nhé. Liên hệ Zalo Admin để hỗ trợ thêm nha!"

    # 5. WEB ĐỂ LÀM GÌ -> Gửi thẻ <a> để nhấn được
    elif any(word in msg for word in ["web", "là gì", "tác dụng", "giới thiệu", "gis"]):
        try:
            url = reverse('gioithieu')
            return (f"Chào bạn, hệ thống GIS-TVTS giúp bạn tra cứu trường học qua bản đồ trực quan. "
                    f"Bạn xem giới thiệu chi tiết tại đây nhé: <a href='{url}' class='chat-link'>Giới thiệu hệ thống</a>.")
        except:
            return "Hệ thống giúp bạn tra cứu trường và ngành học trực quan. Bạn xem phần 'Giới thiệu' để rõ hơn nhé!"

    # 6. CẢM ƠN
    elif any(word in msg for word in ["cảm ơn", "thanks", "tks", "ok"]):
        return "Không có gì nè! Rất vui được hỗ trợ bạn. Chúc bạn ôn thi thật tốt và đậu vào trường mình thích nhé! ❤️"

    # 7. CÁC CÂU HỎI CHI TIẾT (Điểm chuẩn, học phí,...) -> Đẩy về Zalo
    else:
        return ("Cảm ơn câu hỏi của bạn! Với thông tin chi tiết về điểm chuẩn hoặc học phí, "
                "bạn vui lòng liên hệ <b>Zalo Admin</b> để nhận được thông tin chính xác nhất 1:1 nhé. "
                "Chúng mình luôn sẵn sàng hỗ trợ bạn!")