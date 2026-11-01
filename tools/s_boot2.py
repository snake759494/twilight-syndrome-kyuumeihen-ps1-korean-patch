print('title at',goto_title())
time.sleep(2); e.key('o',hold=0.2); time.sleep(12)
for i in range(12):
    e.key('o',hold=0.2); time.sleep(2.5); e.shot('shots/w5.png'); tp=text_present('shots/w5.png')
    if tp>0.01: print('text',i,tp); break
