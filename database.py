execute('''INSERT INTO game_history (user_id, session_id, bet_type, bet_amount, win_amount, dice1, dice2, dice3, total, result) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (user_id, session_id, bet_type, bet_amount, win_amount, dice1, dice2, dice3, total, result))
        self.cursor.execute("UPDATE users SET total_game = total_game + 1 WHERE user_id = ?", (user_id,))
        if win_amount > 0: self.cursor.execute("UPDATE users SET total_win = total_win + ? WHERE user_id = ?", (win_amount, user_id))
        self.conn.commit()
    
    def get_user_stats(self, user_id):
        self.cursor.execute('''SELECT COUNT(*), SUM(bet_amount), SUM(win_amount), COUNT(CASE WHEN win_amount > 0 THEN 1 END) FROM game_history WHERE user_id = ?''', (user_id,))
        row = self.cursor.fetchone()
        return {'games': row[0] or 0, 'total_bet': row[1] or 0, 'total_win': row[2] or 0, 'win_count': row[3] or 0, 'win_rate': round((row[3] / row[0] * 100) if row[0] > 0 else 0, 1)}
    
    def create_gift_code(self, code, amount, created_by):
        self.cursor.execute('''INSERT INTO gift_codes (code, amount, created_by) VALUES (?, ?, ?)''', (code, amount, created_by))
        self.conn.commit()
    
    def use_gift_code(self, user_id, code):
        self.cursor.execute('''SELECT amount, usage_limit, used_count FROM gift_codes WHERE code = ?''', (code,))
        result = self.cursor.fetchone()
        if not result: return False, "Mã không tồn tại!", 0
        amount, usage_limit, used_count = result
        if used_count >= usage_limit: return False, "Mã đã được sử dụng hết!", 0
        self.cursor.execute('''UPDATE gift_codes SET used_count = used_count + 1 WHERE code = ?''', (code,))
        self.conn.commit()
        return True, f"Nhập code thành công +{amount:,} VND!", amount

db = Database()