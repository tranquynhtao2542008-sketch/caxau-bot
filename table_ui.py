class TableUI:
    @staticmethod
    def create_table(headers, rows, title=""):
        if not rows: return "📭 Không có dữ liệu!"
        col_widths = []
        for i in range(len(headers)):
            max_width = len(str(headers[i]))
            for row in rows:
                if i < len(row): max_width = max(max_width, len(str(row[i])))
            col_widths.append(min(max_width, 25))
        border_top = "┏" + "━" * (sum(col_widths) + len(col_widths) * 3 + 1) + "┓"
        border_bottom = "┗" + "━" * (sum(col_widths) + len(col_widths) * 3 + 1) + "┛"
        separator = "┣" + "━" * (sum(col_widths) + len(col_widths) * 3 + 1) + "┫"
        header_line = "┃"
        for i, header in enumerate(headers):
            header_line += f" {header:^{col_widths[i]}} ┃"
        table = f"{border_top}\n"
        if title: table += f"┃ {title:^{sum(col_widths) + len(col_widths) * 3 - 1}} ┃\n{separator}\n"
        table += f"{header_line}\n{separator}\n"
        for row in rows:
            row_line = "┃"
            for i, cell in enumerate(row):
                if i < len(headers): row_line += f" {str(cell)[:col_widths[i]]:^{col_widths[i]}} ┃"
            table += f"{row_line}\n"
        table += border_bottom
        return f"```\n{table}\n```"
    
    @staticmethod
    def profile_table(user_data):
        headers = ["THÔNG TIN", "GIÁ TRỊ"]
        rows = [["🆔 ID", user_data.get('user_id', 'N/A')], ["👤 Tên", user_data.get('username', 'N/A')], ["💰 Số dư", f"{user_data.get('balance', 0):,} VND"], ["⭐ VIP", f"Level {user_data.get('vip_level', 0)}"], ["🎮 Số ván", user_data.get('games', 0)], ["📈 Tỷ lệ thắng", f"{user_data.get('win_rate', 0)}%"], ["🏦 STK", user_data.get('bank', 'Chưa cài')]]
        return TableUI.create_table(headers, rows, "👤 PROFILE NGƯỜI CHƠI")
    
    @staticmethod
    def bet_confirmation_table(bet_type, amount, rate, is_xien):
        headers = ["THÔNG TIN", "GIÁ TRỊ"]
        rows = [["🔄 Cửa cược", bet_type.upper()], ["💰 Số tiền", f"{amount:,} VND"], ["📊 Tỷ lệ", f"x{rate}"], ["🎯 Xiên", "✅" if is_xien else "❌"]]
        return TableUI.create_table(headers, rows, "📌 XÁC NHẬN CƯỢC")