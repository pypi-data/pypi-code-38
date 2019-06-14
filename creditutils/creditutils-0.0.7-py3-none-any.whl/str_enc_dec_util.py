# -*- coding:UTF-8 -*- # 标识为


class StrEncDec(object):
    CHAR_COUNT = 26;
    CHAR_OFFSET_BUTT = CHAR_COUNT*2;
    # 加密时整体向右偏移量
    ENC_CHAR_OFFSET = 13;
    # 解密时整体向右偏移量
    DEC_CHAR_OFFSET = CHAR_OFFSET_BUTT - ENC_CHAR_OFFSET;
    
    STR_KEEP_BUF = list();
    to_append = 'a'; 
    for i in range(CHAR_COUNT):
        STR_KEEP_BUF.append(chr(ord(to_append)+i));
    to_append = 'A'; 
    for i in range(CHAR_COUNT):
        STR_KEEP_BUF.append(chr(ord(to_append)+i));
    
    def get_index(self, char):
        return StrEncDec.STR_KEEP_BUF.index(char)
    
    def get_char(self, index):
        return StrEncDec.STR_KEEP_BUF[index]
    
    def _enc_dec_base(self, src_str, offset):
        dst_list = list()
        for src_char in src_str:
            try:
                src_index = self.get_index(src_char)
                dst_index = (src_index + offset) % StrEncDec.CHAR_OFFSET_BUTT
                dst_list.append(self.get_char(dst_index))
            except ValueError:
                dst_list.append(src_char)
        return ''.join(dst_list)
    
    def encrypt(self, src_str):
        return self._enc_dec_base(src_str, StrEncDec.ENC_CHAR_OFFSET)
    
    def decrypt(self, src_str):
        return self._enc_dec_base(src_str, StrEncDec.DEC_CHAR_OFFSET)

if __name__ == '__main__':
    enc_dec = StrEncDec()
    src_str = 'what are you doing here and who you are?'
    print(src_str)
    enc_str = enc_dec.encrypt(src_str)
    print(enc_str)
    dec_str = enc_dec.decrypt(enc_str)
    print(dec_str)