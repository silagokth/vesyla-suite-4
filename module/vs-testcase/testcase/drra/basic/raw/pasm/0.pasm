epoch <ep0> {
    cell  (x=0, y=0) {
        raw {
            wait  (cycle=6)
            dsu  (slot=1, port=2, init_addr=0)
            rep  (slot=1, port=2, iter=3, step=1, delay=0)
            dsu  (slot=1, port=0, init_addr=0)
            rep  (slot=1, port=0, level=0, iter=1, step=2, delay=0)
            rep  (slot=1, port=0, level=1, iter=1, step=1, delay=0)
            route  (slot=0, option=0, sr=0, source=2, target=128)
            dsu  (slot=2, port=3, init_addr=0)
            rep  (slot=2, port=3, iter=3, step=1, delay=0)
            act  (mode=0, param=0, ports=0b0000000001010100)
            act  (mode=0, param=2, ports=0b0000000000001000)
            wait  (cycle=38)
        }
    }
    cell  (x=1, y=0) {
        raw {
            dpu  (slot=4, mode=7)
            swb  (slot=0, option=0, channel=4, source=1, target=4)
            swb  (slot=0, option=0, channel=5, source=2, target=5)
            swb  (slot=0, option=0, channel=3, source=4, target=3)
            route  (slot=0, option=0, sr=1, source=1, target=6)
            route  (slot=0, option=0, sr=0, source=3, target=128)
            dsu  (slot=1, port=2, init_addr=0)
            rep  (slot=1, port=2, iter=1, step=1, delay=1)
            dsu  (slot=2, port=2, init_addr=0)
            rep  (slot=2, port=2, iter=1, step=1, delay=1)
            dsu  (slot=2, port=1, init_addr=0)
            rep  (slot=2, port=1, iter=31, step=1, delay=0)
            dsu  (slot=1, port=1, init_addr=0)
            rep  (slot=1, port=1, iter=31, step=1, delay=0)
            dsu  (slot=3, port=0, init_addr=0)
            act  (mode=0, param=4, ports=0b0000000000000001)
            act  (mode=0, param=0, ports=0b0000000000000101)
            act  (mode=0, param=1, ports=0b0000000000000100)
            act  (mode=0, param=2, ports=0b0000000000000100)
            act  (mode=0, param=1, ports=0b0000000000100010)
            rep  (slot=3, port=0, iter=31, step=1, delay=0)
            act  (mode=0, param=3, ports=0b0000000000000001)
            wait  (cycle=27)
            dsu  (slot=3, port=3, init_addr=0)
            rep  (slot=3, port=3, iter=1, step=1, delay=0)
            act  (mode=0, param=3, ports=0b0000000000001000)
            wait  (cycle=2)
        }
    }
    cell  (x=2, y=0) {
        raw {
            wait  (cycle=13)
            route  (slot=0, option=0, sr=1, source=1, target=4)
            act  (mode=0, param=0, ports=0b0000000000000100)
            wait  (cycle=30)
            dsu  (slot=2, port=2, init_addr=0)
            rep  (slot=2, port=2, iter=1, step=1, delay=0)
            dsu  (slot=1, port=1, init_addr=0)
            rep  (slot=1, port=1, iter=1, step=1, delay=0)
            dsu  (slot=1, port=3, init_addr=0)
            rep  (slot=1, port=3, iter=1, step=1, delay=0)
            act  (mode=0, param=2, ports=0b0000000000000100)
            act  (mode=0, param=1, ports=0b0000000000001010)
            wait  (cycle=0)
        }
    }
}
