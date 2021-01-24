.open "ShitoData/repack/bank_14.bin"
    ; Jump to custom code from the code redirect function
    .org 0x82cf
    jmp 0xf759
    nop
    ; Custom code to check if a character is a control code or ascii
    ; If < 0xff20, assume this is a control code
    .org 0xf759
    cmp si,0xff20
    jge ascii
    and si,0x00ff
    jmp 0x82d3
    ascii:
    jmp 0x82db

    ; Tweak start x position for lines
    .org 0x83cc
    mov word ss:0x41c,0x0
    .org 0x83de
    mov word ss:0x41c,0x0

    ; Replace the default state of the name input screen to the third one with ASCII
    .org 0xbe7e
    call 0xf860

    ; Don't allow the cursor to go to the name input type selection on the left
    ; Since we just use 1 screen
    .org 0xbef2
    mov ax,0x10
    .org 0xbf0f
    mov ax,0x0

    ; Jump to custom code from the character drawing function
    .org 0x82db
    call 0xf790

    ; Replace other calls to the drawing function
    .org 0x8438
    inc di
    inc di
    call 0xf770
    nop
    nop
    .org 0x8496
    inc di
    inc di
    call 0xf770
    nop
    nop
    .org 0x84f1
    inc di
    inc di
    call 0xf770
    nop
    nop

    ; Replace hardcoded BIN string calls
    .org 0x2d3f
    inc di
    inc di
    call 0xf7b0
    .org 0x55a8
    inc di
    inc di
    call 0xf7b0
    .org 0xa371
    inc di
    inc di
    call 0xf7b0
    .org 0xae1f
    inc di
    inc di
    call 0xf7b0
    .org 0xbc2e
    inc di
    inc di
    call 0xf7b0
    .org 0xbc4d
    inc di
    inc di
    call 0xf7b0
    .org 0xbc67
    inc di
    inc di
    call 0xf7b0
    .org 0xe3a6
    inc di
    inc di
    call 0xf7b0
    .org 0xe3c5
    inc di
    inc di
    call 0xf7b0
    .org 0xe3df
    inc di
    inc di
    call 0xf7b0
    .org 0xe40b
    inc di
    inc di
    call 0xf7b0
    .org 0xe799
    inc di
    inc di
    call 0xf7b0

    ; Name input rendering call
    .org 0xc1db
    inc di
    inc di
    call 0xf880
    pop cx

    ; Render other character
    .org 0xf770
    push cx
    call 0xf800
    test cx,cx
    je return
    ; Decrease di by 1
    dec di
    return:
    pop cx
    push di
    call 0x142e
    pop di
    ret

    ; Render script character
    .org 0xf790
    push cx
    call 0xf800
    test cx,cx
    je return
    ; Decrease script counter by 1
    dec word ds:[bx+0x0022]
    return:
    pop cx
    call 0x142e
    ret

    ; Render bin character
    .org 0xf7b0
    push cx
    call 0xf800
    test cx,cx
    je return
    ; Decrease di by 1
    dec di
    return:
    pop cx
    call 0x17e2
    ret

    ; Convert si to ASCII character
    .org 0xf800
    mov ax,si
    mov cx,0x0
    ; Jump to return it's not an ascii byte
    and ax,0xff
    cmp ax,0x20
    jb return
    cmp ax,0x40
    je return
    cmp ax,0x80
    je return
    cmp ax,0xc0
    jge return
    ; Convert ascii to code
    sub ax,0x20
    ; Multiply by 4, and shift by 4
    shl ax,0x6
    ; Add the first glyph number and move to si
    add ax,0xa300
    mov si,ax
    ; Set cx to 1
    mov cx,0x1
    return:
    ret

    ; Initialize the character selection screen to the third one
    .org 0xf860
    mov word ds:[bx+0x34],ax
    mov ax,0x4
    mov word ds:[bx+0x20],ax
    mov word ds:[bx+0x22],ax
    mov ax,0xc42c
    mov word ds:[bx+0x24],ax
    mov ax,0x0
    ret

    ; Space out the name rendering characters
    .org 0xf880
    add word ss:[0x300],0x2
    push word ss:[0x300]
    call 0x17e2
    pop word ss:[0x300]
    add word ss:[0x300],0xb
    ret
.close
