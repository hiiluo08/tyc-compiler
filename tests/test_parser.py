"""
Parser test cases for TyC compiler
TODO: Implement 100 test cases for parser
"""

import pytest
from tests.utils import Parser

def test_001():
    source = """
void main() {
    printString("Hello, World!");
}
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_002():
    source = """
int add(int x, int y) {
    return x + y;
}

int multiply(int x, int y) {
    return x * y;
}

void main() {
    auto a = readInt();
    auto b = readInt();
    
    auto sum = add(a, b);
    auto product = multiply(a, b);
    
    printInt(sum);
    printInt(product);
}
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_003():
    source = """
void main() {
    auto n = readInt();
    auto i = 0;
    
    while (i < n) {
        printInt(i);
        ++i;
    }
    
    for (auto j = 0; j < n; ++j) {
        if (j % 2 == 0) {
            printInt(j);
        }
    }
}
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_004():
    source = """
int factorial(int n) {
    if (n <= 1) {
        return 1;
    } else {
        return n * factorial(n - 1);
    }
}

void main() {
    auto num = readInt();
    auto result = factorial(num);
    printInt(result);
}
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_005():
    source = """
void main() {
    // With auto and initialization
    auto x = readInt();
    auto y = readFloat();
    auto name = readString();
    
    // With auto without initialization
    auto sum;
    sum = x + y;              // sum: float (inferred from first usage - assignment)
    
    // With explicit type and initialization
    int count = 0;
    float total = 0.0;
    string greeting = "Hello, ";
    
    // With explicit type without initialization
    int i;
    float f;
    i = readInt();            // assignment to int
    f = readFloat();          // assignment to float
    
    printFloat(sum);
    printString(greeting);
    printString(name);
    
    // Note: String concatenation is NOT supported
    // This is because + operator applies to int or float, not string
}
"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_006():
    source ="""
struct Point {
    int x;
    int y;
};

struct Person {
    string name;
    int age;
    float height;
};

void main() {
    // Struct variable declaration without initialization
    Point p1;
    p1.x = 10;
    p1.y = 20;
    
    // Struct variable declaration with initialization
    Point p2 = {30, 40};
    
    // Access and modify struct members
    printInt(p2.x);
    printInt(p2.y);
    
    // Struct assignment
    p1 = p2;  // Copy all members
    
    // Person struct usage
    Person person1 = {"John", 25, 1.75};
    printString(person1.name);
    printInt(person1.age);
    printFloat(person1.height);
    
    // Modify struct members
    person1.age = 26;
    person1.height = 1.76;
    
    // Using struct with auto
    auto p3 = p2;  // p3: Point (inferred from assignment)
    printInt(p3.x);
}
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_007():
    source = """
void main() {
"""
    expected = "Error on line 3 col 0: <EOF>"
    assert Parser(source).parse() == expected

def test_008():
    source = """
void main {}
"""
    expected = "Error on line 2 col 10: {"
    assert Parser(source).parse() == expected


def test_022():
        source = """
    void main () {
        return a++--++--;
        return ++--++--a++--++--;
    }
    """
        expected = "success"
        assert Parser(source).parse() == expected

def test_024():
        source = """
    void main () {
        return {1+3, "s"++};
    }
    """
        expected = "success"
        assert Parser(source).parse() == expected
        
def test_028():
        source = """
    void main () {
        a.foo();
    }
    """
        expected = "Error on line 3 col 9: ("
        assert Parser(source).parse() == expected

def test_029():
        source = """
    void main () {
        foo.a.b;
        ++a.b;
        a.b++;
    }
    """
        expected = "success"
        assert Parser(source).parse() == expected
        
def test_037():
        source = """
    void main () {
        foo().b = 2;
    }
    """
        expected = "Error on line 3 col 9: ."
        assert Parser(source).parse() == expected
        
def test_038():
        source = """
    void main () {
        ++a = 1;
    }
    """
        expected = "Error on line 3 col 8: ="
        assert Parser(source).parse() == expected
        
def test_047():
        source = """
    void main () {
        return ;
        return 1 +2 *++3;
    }
    """
        expected = "success"
        assert Parser(source).parse() == expected
        
def test_057():
        source = """
    void main () {
       for(; ; -a) continue;
    }
    """
        expected = "Error on line 3 col 11: -"
        assert Parser(source).parse() == expected
        
def test_067():
        source = """
    void main () {
        switch (1 *3 / 4) {
            default:
                1;
            case 2:
                 2;
        }
    
        switch (1 *3 / 4) {
            case 3:1;
            default:1;
            case 2: 2;
        }
    }
    """
        expected = "success"
        assert Parser(source).parse() == expected
        
def test_089():
        source = """
    void main(){
        T a = b;
        True a = b;
        true c = f;
        F b = T;
    }
    """
        expected = "success"
        assert Parser(source).parse() == expected
        
def test_094():
        source = """
    void main(){
        switch (x) { }
    }
    """
        expected = "success"
        assert Parser(source).parse() == expected        

def test_097():
        source = """
    main(){for(a * 3; i * 2; a++ = 2 = 3) {return ;}}
    """
        expected = "Error on line 2 col 13: *"
        assert Parser(source).parse() == expected
        
def test_108():
        source = """
    void main () {
        auto x = readInt();
        switch (x) {
            default:
                printInt(0);
            default:
                printInt(0);
        }
    }
    """
        expected = "Error on line 7 col 8: default"
        assert Parser(source).parse() == expected
        
def test_116():
        source = """
    void main () {
       {1, 2}.b;
    }
    """
        expected = "Error on line 3 col 9: ."
        assert Parser(source).parse() == expected