from router import Router
import router as rt

KEY = b"anotherkey123456"

if __name__ == '__main__':
    router = Router(rt.R2_PORT, rt.R3_PORT, KEY)
    router.start()
    
