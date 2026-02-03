import pytest
from tests.utils import Parser

def test_000():
    """Simple entry point"""
    source = """
    """
    expected = "Error on line 2 col 4: <EOF>"
    assert Parser(source).parse() == expected

def test_001():
    """Simple entry point"""
    source = """
    void main() {
        int a = 5;
    }
    """
    expected = "success"
    assert Parser(source).parse() == expected

def test_002():
    """Test function declaration"""
    source = """
    int add(int a, int b) {
        return a + b;
    }
    """
    expected = "success"
    assert Parser(source).parse() == expected

def test_003():
    """Test function declaration"""
    source = """
    add(int a, int b) {     // omit return type
        return a + b;
    }
    """
    expected = "success"
    assert Parser(source).parse() == expected

def test_004():
    """Test function declaration"""
    source = """
    int add(int a, b; float c) {  
        return a + b + c;
    }
    """
    expected = "Error on line 2 col 20: ;"
    assert Parser(source).parse() == expected

def test_005():
    """Test function declaration"""
    source = """
    int foo(int a, float b, string c, D d) {}   // must have statement
    """
    expected = "Error on line 2 col 44: }"
    assert Parser(source).parse() == expected

def test_006():
    """Test function declaration"""
    source = """
    int foo(auto a) {return a;}  // cannot use auto for parameter type
    """
    expected = "Error on line 2 col 12: auto"
    assert Parser(source).parse() == expected

def test_007():
    """Test function declaration"""
    source = """
    int foo(int a, int b);
    """
    expected = "Error on line 2 col 25: ;"
    assert Parser(source).parse() == expected

def test_008():
    """Test function declaration"""
    source = """
    int foo(int a, int b) {return a + b;}
    float foo1(float a, float b) {return a + b;}
    string foo2(string a, string b){return a;}
    foo3(int a, float b, string c){return a + b;}
    auto foo4() {return 1;}
    """
    expected = "Error on line 6 col 4: auto"
    assert Parser(source).parse() == expected

def test_009():
    """Test function declaration"""
    source = """
    // Return type inferred as int
    add(int x, int y) {
        return x + y;
    }

    // Return type inferred as float
    multiply(float a, float b) {
        return a * b;
    }

    // Return type inferred as void (no return statement)
    greet(string name) {
        printString("Hello, ");
        printString(name);
    }

    void main() {
        auto sum = add(3, 5);              // sum: int
        auto product = multiply(2.5, 3.0);  // product: float
        greet("World");
    }
    """
    expected = "success"
    assert Parser(source).parse() == expected

def test_010():
    """Test variable declaration"""
    source = """
    void main() {
        int a = 5;
        float b = 3.0;
        string c = "hello";
        auto d = 4;
    }
    """
    expected = "success"
    assert Parser(source).parse() == expected

def test_011():
    """Test struct declaration"""
    source = """
    struct A {
        int a;
        float b;
        string d;
    };
    """
    expected = "success"
    assert Parser(source).parse() == expected

def test_012():
    """Test struct declaration"""
    source = """
    struct A {};
    """
    expected = "success"
    assert Parser(source).parse() == expected

def test_013():
    """Test struct declaration"""
    source = """
    A foo() {return {{1, 2}, 2};}
    int main() {
        foo().a;
    }
    """
    expected = "Error on line 4 col 13: ."
    assert Parser(source).parse() == expected

def test_014():
    source = """
void main() {
    printString("Hello, World!");
}
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_015():
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

def test_016():
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

def test_017():
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

def test_018():
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


def test_019():
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

def test_020():
    source = """
void main() {
"""
    expected = "Error on line 3 col 0: <EOF>"
    assert Parser(source).parse() == expected

def test_021():
    source = """
void main {
A a = {};
a = {1, 2, 3};
}
"""
    expected = "Error on line 2 col 10: {"
    assert Parser(source).parse() == expected

def test_022():
    source = """
    struct A {
        auto a;
    }
"""
    expected = "Error on line 3 col 8: auto"
    assert Parser(source).parse() == expected


def test_023():
    source = """
    struct A {
        int a = 10;
    }
"""
    expected = "Error on line 3 col 14: ="
    assert Parser(source).parse() == expected

def test_024():
    source = """
    struct A {
        int a, b, c;
    }
"""
    expected = "Error on line 3 col 13: ,"
    assert Parser(source).parse() == expected

def test_025():
    source = """
    struct A {
        int a;
        float b;
        struct C {
            int d;
        };
    };
"""
    expected = "Error on line 5 col 8: struct"
    assert Parser(source).parse() == expected

def test_026():
    source = """
    struct A {
        void b;
    };
"""
    expected = "Error on line 3 col 8: void"
    assert Parser(source).parse() == expected

def test_027():
    source = """
    struct A {
        int foo(){
            return 1;
        }
    };
"""
    expected = "Error on line 3 col 15: ("
    assert Parser(source).parse() == expected

def test_028():
    source = """
    struct A {
        int a;
        if(a > 0) {
            a++;
        }
    };
"""
    expected = "Error on line 4 col 8: if"
    assert Parser(source).parse() == expected

def test_029():
    source = """
    struct A {
        int value;
    };
    struct B {
        A obj;
    };
    void main() {
        B b;
        b.obj.value = 10;
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_030():
    source = """
    struct A {
        int value;
        struct B;
    };
"""
    expected = "Error on line 4 col 8: struct"
    assert Parser(source).parse() == expected

def test_031():
    source = """
    struct A {
        int a;
        int b;
        float c;
    };
    void main() {
        A a = {1, 2, 3};
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_032():
    source = """
    struct A {
        int a;
        int b;
        float c;
    };
    void main() {
        A a = {(a = 1), foo(), 3 + 1 % 2, b, {2., 3, {5}}};
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_033():
    source = """
    void main() {
        A a = {(a = 1), foo(), 3 + 1 % 2, b, {2., 3, {5}}};
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_034():
    source = """
    void main() {
        A a = {(a = 1), foo(), 3 + 1 % 2, b, {2., 3, {5}}};
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_035():
    source = """
    int foo(int i) {
        return i++;
    }
    void main() {
        for(int i = 0; i < 10; foo(i)){
            foo() = 1;
        }
    }
"""
    expected = "Error on line 6 col 37: )"
    assert Parser(source).parse() == expected

def test_036():
    source = """
    struct A {
        int a;
        int b;
        void init(int a_a, int b_b){
            a = a_a;
            b = b_b;
        }
    }
    void main() {}
"""
    expected = "Error on line 5 col 8: void"
    assert Parser(source).parse() == expected

def test_037():
    source = """
    struct A {
        int a;
        int b;
        void init(int a_a, int b_b){
            a = a_a;
            b = b_b;
        }
    }
    void main() {}
"""
    expected = "Error on line 5 col 8: void"
    assert Parser(source).parse() == expected

def test_038():
    source = """
    void main() {
        auto a = 5;
        {
            auto a = "hello";
            {
                auto a = 3.14;
                {
                    auto a = {1, 2, 3};
                }
            }
        }
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_039():
    source = """
    void main() {
        {} {} {}
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_040():
    source = """
    void main() {
        { int a = 4;
    }
"""
    expected = "Error on line 5 col 0: <EOF>"
    assert Parser(source).parse() == expected

def test_041():
    source = """
    void main() {
        int a = 4;
        {
            if(a > 0){
                {
                    for(a = 4; a < 9; a++){
                        {
                            while(a < 7) {
                                {
                                    switch(a){
                                        {
                                        
                                        }
                                    }
                                }
                            }   
                        }
                    }
                }
            }
        }
    }
"""
    expected = "Error on line 12 col 40: {"
    assert Parser(source).parse() == expected

def test_042():
    source = """
    void main() {
        if(0) {
            printString("Hello");
        }
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_043():
    source = """
    void main() {
        if(0) {
            printString("Hello");
        } else {
            printString("BK");
        }
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_043_1():
    source = """
    void main() {
        if(a > 0) if (b > 0) a; else b;
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_044():
    source = """
    void main() {
        string day = "Tuesday";
        if(day == "Monday") {
            printString("Monday");
        } else if(day == "Tuesday") {
            printString("Tuesday");
        } else if(day == "Wednesday") {
            printString("Wednesday");
        } else if(day == "Thursday") {
            printString("Thursday");
        } else if(day == "Friday") {
            printString("Friday");
        } else if(day == "Saturday") {
            printString("Saturday");
        } else if(day == "Sunday") {
            printString("Sunday");
        } else {
            printString("Error");
        }
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_044():
    source = """
    void main() {
        if (a > 0) printInt(a); else printInt(1);
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_045():
    source = """
    void main() {
        if (a > 0)
            if (b > 0)
                if (c > 0)
                    if (d > 0)
                        if (e > 0)
                            printInt(a + b + c + d + e);
                        else printInt(e);
                    else printInt(d);
                else printInt(c);
            else printInt(b);
        else printInt(a);
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_046():
    source = """
    void main() {
        if (a > 0) printInt(a); else a = -a; else printInt(-a);
    }
"""
    expected = "Error on line 3 col 45: else"
    assert Parser(source).parse() == expected

def test_047():
    source = """
    void main() {
        if () {
            printString("hello world");
        }
    }
"""
    expected = "Error on line 3 col 12: )"
    assert Parser(source).parse() == expected

def test_048():
    source = """
    void main() {
        if () {
            printString("hello world");
        }
    }
"""
    expected = "Error on line 3 col 12: )"
    assert Parser(source).parse() == expected

def test_049():
    source = """
    void main() {
        for(;;){
            printString("hello");
        }
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_049():
    source = """
    void main() {
        for(;;){
            printString("hello");
        }
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_050():
    source = """
    void main() {
        for(int i = 0;;){
            if (i < 5) break;
            printInt(i);
            i++;
        }
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_050():
    source = """
    void main() {
        int i;
        for(i = 0;;){
            if (i < 5) break;
            printInt(i);
            i++;
        }
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_051():
    source = """
    void main() {
        for(auto i = 10; i < 0; --i){
            if (i < 5) break;
            printInt(i);
            i++;
        }
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_052():
    source = """
    void main() {
        int i = 0;
        for(; i < 6 ;i++){
            printInt(i);
        }
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_053():
    source = """
    int inc(int i){
        return ++i;
    }
    int compare(int a, int b){ return a < b; }
    void main() {
        int i = 0;
        for(; compare(i, 6) ; inc(i)){
            printInt(i);
        }
    }
"""
    expected = "Error on line 8 col 36: )"
    assert Parser(source).parse() == expected

def test_054():
    source = """
    int inc(int i){
        return ++i;
    }
    int compare(int a, int b){ return a < b; }
    void main() {
        int i = 0;
        for(; compare(i, 6) ; inc(i)){
            printInt(i);
        }
    }
"""
    expected = "Error on line 8 col 36: )"
    assert Parser(source).parse() == expected

def test_055():
    source = """
    void main() {
        int i = 0;
        for(i = 0; i < 10; a = a + 1){
            printInt(i);
        }
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_056():
    source = """
    void main() {
        int a = 5;
        int b = 0;
        switch(a){
            case 1:
                b = 1;
                printInt(b);
                break;
            case 2:
                b = 2;
                printInt(b % 2);
                break;
            case 3:
                b = 3;
                printInt(b != 0);
                break;
            default:
                printInt(b + 1);
                break;
        }
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_056():
    source = """
    void main() {
        auto a = 5;
        switch(a){
            case -5: a++;
            case -4: a++;
            case -3: a++;
            case -2: a++;
            case -1: a++;
            case 0: a++;
            default: break;
        }
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_057():
    source = """
    void main() {
        auto a = 5;
        switch(a){
            case 1: 
            case 2:
            case 4:
            case 5: 
                printInt(a);
                break;
        }
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_058():
    source = """
    void main() {
        auto a = 5;
        switch(a){
            case : 
            case 2:
            case 4:
            case 5: 
                printInt(a);
                break;
        }
    }
"""
    expected = "Error on line 5 col 17: :"
    assert Parser(source).parse() == expected

def test_059():
    source = """
    void main() {
        auto a = 5;
        switch(a){
            default 1:
                break;
        }
    }
"""
    expected = "Error on line 5 col 20: 1"
    assert Parser(source).parse() == expected

def test_060():
    source = """
    void main(){
        auto i = 0;
        while (i < 10) {
            printInt(i);
            ++i;
        }
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_061():
    source = """
    struct A {
        int a;
    }
    struct B {
        A a;
        int b;
    }
    void main(){
        B b;
        b.a.2 = 10;
    }
"""
    expected = "Error on line 5 col 4: struct"
    assert Parser(source).parse() == expected

def test_062():
    source = """
    void main(){
        a + b; a - b; a * b; a / b; a % b;
        a == b; a < b; a > b; a >= b; a <= b;
        a && b; a || b; !a; ++a; --a;
        a++; a--;
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_063():
    source = """
    void main(){
        a = b = c = f || g && h;
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_064():
    source = """
    void main(){
        a == d != e != f > g;
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_065():
    source = """
    void main(){
        a == d != e != f > g;
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_066():
    source = """
    void main(){
        a < b >= c <= d == e;
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_067():
    source = """
    void main(){
        a < b >= c <= d == e;
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_068():
    source = """
    void main(){
        a < b >= c <= d == e;
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_069():
    source = """
    void main(){
        a + ++--a--++;
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_070():
    source = """
    void main(){
        ++!a--;
    }
"""
    expected = "Error on line 3 col 10: !"
    assert Parser(source).parse() == expected

def test_071():
    source = """
    void main(){
        +++a;
    }
"""
    expected = "Error on line 3 col 10: +"
    assert Parser(source).parse() == expected

def test_072():
    source = """
    void main(){
        + ++a;
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_073():
    source = """
    void main(){
        ++a.b.c;
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_074():
    source = """
    void main(){
        a.b.c++;
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_075():
    source = """
    void main(){
        fooA().b;
    }
"""
    expected = "Error on line 3 col 14: ."
    assert Parser(source).parse() == expected
    
def test_076():
    source = """
    void main(){
        !foo()++;
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_077():
    source = """
    void main(){
        fooA().b = 1;
    }
"""
    expected = "Error on line 3 col 14: ."
    assert Parser(source).parse() == expected

def test_078():
    source = """
    auto foo(int a, int b){
        return a + b;
    }
    void main(){
    }
"""
    expected = "Error on line 2 col 4: auto"
    assert Parser(source).parse() == expected

def test_079():
    source = """
    foo(int a, int b){}
"""
    expected = "Error on line 2 col 22: }"
    assert Parser(source).parse() == expected

def test_079():
    source = """
    foo(int a, b, c){ return; }
"""
    expected = "Error on line 2 col 16: ,"
    assert Parser(source).parse() == expected

def test_080():
    source = """
    int a;
"""
    expected = "Error on line 2 col 9: ;"
    assert Parser(source).parse() == expected

def test_081():
    source = """
    void main() {
        for(int i = 0; i < 10; i++){
            if(i == 5) continue;
            else if(i >= 7) break;
        }
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_082():
    source = """
    foo(int a){
        if (a < 0) return "Hello";
        else if (a > 1) return 1;
    }
    void main() {
        int a = foo(-1);
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_083():
    source = """
    void main() {
        int a = b = c = 10;
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_084():
    source = """
    void main() {
        int a = b = 10 + 7;
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_085():
    source = """
    void main() {
        for(int i = 0; i < 10; i++) printInt(i);
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_086():
    source = """
    void main() {
        void a;
    }
"""
    expected = "Error on line 3 col 8: void"
    assert Parser(source).parse() == expected

def test_087():
    source = """
    void main() {
        (((a + b) / c) * d + (e / (f % g)));
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_088():
    source = """
    void main() {
        (a + (b - c + (++a - b / 2)));
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_089():
    source = """
    void main() {
        (a + (b - c + (++a - b / 2)));
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_090():
    source = """
    void main() {
        int a = 0;
        while(a < 10){}
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_091():
    source = """
    void main() {
        int i = 0;
        for(i = 0; i < 10; ++i){}
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_092():
    source = """
    // Linked list declaration
    struct Node {
        int value;
        Node next;
    };
    struct IList {
        Node head;
        Node tail;
    };
    void main() {
        Node a = {5, null};
        Node b = {3, null};
        IList ll = {a, b}; 
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_093():
    source = """
    // Linked list declaration
    struct A {
        int a;
        int b; 
        int c;
        int d;
        int e;
    };
    void main() {
        A a = {1, 2, , , 5};
    }
"""
    expected = "Error on line 11 col 21: ,"
    assert Parser(source).parse() == expected

def test_094():
    source = """
    // Linked list declaration
    struct A {
        int a;
        int b; 
        int c;
        int d;
        int e;
    };
    void main() {
        A a = {1, 2, , , 5};
    }
"""
    expected = "Error on line 11 col 21: ,"
    assert Parser(source).parse() == expected

def test_095():
    source = """
    void main() {
        // Coercion float to int value
        int a = int(3.5);
    }
"""
    expected = "Error on line 4 col 16: int"
    assert Parser(source).parse() == expected

def test_096():
    source = """
    int foo(int a = 1, int b){
        return a + b;
    }
    void main() {
        // Coercion float to int value
        printInt(foo(2));
    }
"""
    expected = "Error on line 2 col 18: ="
    assert Parser(source).parse() == expected

def test_097():
    source = """
    void main() {
        // Short circuit evaluation
        if((a == 4) && b > a){
            printInt(a);
        }
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected


def test_098():
    source = """
    void main() {
        ;
    }
"""
    expected = "Error on line 3 col 8: ;"
    assert Parser(source).parse() == expected

def test_099():
    source = """
    void main() {
        int a = 0;
        while(a < 5) {
            printInt(a);
            a++;
        } else {
            printString("Hello \"Tien\"");
        }
    }
"""
    expected = "Error on line 7 col 10: else"
    assert Parser(source).parse() == expected

def test_100():
    source = """
    void main() {
        int _int = 1;
        printInt(_int);
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_101():
    source = """
    void main() {
        A a = {1};
        a.x+++++a.x;
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_102():
    source = """
    void main() {
        // Multiple default case in switch statement
        switch(a) {
            default:
                printInt(1);
            default:
                printInt(2);
        }
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_103():
    source = """
    void main() {
        (1 + 2)++;
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected

def test_104():
    source = """
    struct A { int x; };

    int f(int x) {
        for (auto i = 0; i < x; ++i)
            if (i % 2 == 0)
                continue;
            else
                break;
        return x;
    }

    void main() {
        A a = {1};
        f(a.x++);
    }
"""
    expected = "success"
    assert Parser(source).parse() == expected