from router import Router
import router as rt

KEY = b"myfinalkey123456"

if __name__ == '__main__':
    router = Router(rt.R3_PORT, 10_000, KEY)
    router.start()
    
