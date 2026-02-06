from tests.utils import Parser

# Test 64
source_64 = """
    foo(){
        for(int i = 0; i < 10; foo(i)++){
            FAH().x = 1;
        }
        for(int i = 0; i < 10; foo(i)){
            FAH().x = 1;
        }
    }
    void main(){ 
        foo();
    }
"""

print("Test 64 actual output:")
print(Parser(source_64).parse())
print()

# Test 82
source_82 = """
void main(){
    for (; ; (i)++) {
        switch ((a + b) * (c - d)) {
            case 1 + 2:
                foo();
            case (3 * 4):
                bar();
                break;
            default:
                baz();
        }
    }
}
"""

print("Test 82 actual output:")
print(Parser(source_82).parse())
