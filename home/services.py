def get_ai_response(user_message):
    msg = user_message.lower()
    
    # Bộ não ảo: Quét từ khóa để trả lời như người thật
    if any(word in msg for word in ["chào", "hi", "hello"]):
        return "Chào bạn! Mình là trợ lý ảo GIS-TVTS. Bạn cần mình tư vấn về trường ĐH hay ngành học nào không?"
        
    elif "điểm chuẩn" in msg or "bao nhiêu điểm" in msg:
        return "Điểm chuẩn năm nay đang có xu hướng biến động nhẹ. Bạn định thi khối nào để mình tư vấn sát hơn?"
        
    elif "ngành" in msg or "học gì" in msg:
        return "Hiện tại các ngành như Công nghệ thông tin, Logistics và Marketing đang rất hot. Bạn đã làm bài khảo sát định hướng của chúng mình chưa?"
        
    elif "học phí" in msg:
        return "Học phí tùy thuộc vào từng hệ đào tạo (đại trà hay chất lượng cao). Thường dao động từ 15-40 triệu/năm. Bạn quan tâm trường nào?"
        
    elif "tốt nhất" in msg or "nên chọn" in msg:
        return "Việc chọn trường 'tốt nhất' phụ thuộc vào năng lực và tài chính của bạn. Hãy cho mình biết điểm thi dự kiến của bạn nhé!"

    elif "cảm ơn" in msg or "thanks" in msg:
        return "Không có gì nè! Chúc bạn chọn được ngôi trường mơ ước nhé. Cần gì cứ hỏi mình!"

    # Câu trả lời mặc định khi không quét được từ khóa
    else:
        return f"Câu hỏi '{user_message}' rất hay. Theo dữ liệu từ GIS-TVTS, thông tin này đang được cập nhật. Bạn có muốn mình gợi ý các trường có ngành tương tự không?"