from lexer import Lexer, LexerError

DEMO = r'''
glob { var x y }
proc { }
func { }
main {
  var { local { } }
  print "Hello123"
  a = 0;
  while (neg 1) { halt }
  if (eq 1 1) { print "ok" } else { halt }
}
'''.strip()

def run_demo():
    print("== Source ==")
    print(DEMO)
    print("\n== Tokens ==")
    try:
        for tok in Lexer(DEMO):
            print(tok)
    except LexerError as e:
        print(e)

if __name__ == "__main__":
    run_demo()
