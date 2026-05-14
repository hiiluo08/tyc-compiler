"""
Test cases for TyC code generation.

Each test compiles TyC source text through the full pipeline:
  source -> lexer -> parser -> AST -> static check -> Jasmin -> JVM -> stdout

Output is stripped of leading/trailing whitespace by the harness.
"""

import os
import sys

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.utils import ASTGenerator, Checker, CodeGenerator


def run(src, input_data=""):
    ast = ASTGenerator(src).generate()
    return CodeGenerator().generate_and_run(ast, input_data=input_data)


# ============================================================================
# 1. Literals & print (001-010)
# ============================================================================

def test_001():
    """print simple string"""
    assert run('void main() { printString("Hello World"); }') == "Hello World"


def test_002():
    """print positive int"""
    assert run("void main() { printInt(42); }") == "42"


def test_003():
    """print zero"""
    assert run("void main() { printInt(0); }") == "0"


def test_004():
    """print negative int via unary minus"""
    assert run("void main() { printInt(-7); }") == "-7"


def test_005():
    """print float with fraction"""
    assert run("void main() { printFloat(3.14); }") == "3.14"


def test_006():
    """print whole-number float retains .0"""
    assert run("void main() { printFloat(42.0); }") == "42.0"


def test_007():
    """print negative float"""
    assert run("void main() { printFloat(-2.5); }") == "-2.5"


def test_008():
    """print empty string"""
    assert run('void main() { printString(""); }') == ""


def test_009():
    """print large int"""
    assert run("void main() { printInt(1000000); }") == "1000000"


def test_010():
    """two print statements concatenate (no newline between)"""
    assert run('void main() { printString("a"); printString("b"); }') == "ab"


# ============================================================================
# 2. Variables & assignment (011-019)
# ============================================================================

def test_011():
    """int var declaration and read"""
    assert run("void main() { int x = 10; printInt(x); }") == "10"


def test_012():
    """float var declaration and read"""
    assert run("void main() { float x = 1.5; printFloat(x); }") == "1.5"


def test_013():
    """string var declaration and read"""
    assert run('void main() { string s = "abc"; printString(s); }') == "abc"


def test_014():
    """reassignment of int var"""
    assert run("void main() { int x = 1; x = 99; printInt(x); }") == "99"


def test_015():
    """auto type from int init"""
    assert run("void main() { auto x = 7; printInt(x); }") == "7"


def test_016():
    """auto type from float init"""
    assert run("void main() { auto x = 2.25; printFloat(x); }") == "2.25"


def test_017():
    """auto type from string init"""
    assert run('void main() { auto s = "auto"; printString(s); }') == "auto"


def test_018():
    """assignment expression used in a larger expression"""
    assert run("void main() { int a = 0; printInt((a = 4) + 1); }") == "5"


def test_019():
    """copy one variable into another"""
    assert run("void main() { int a = 3; int b = a; printInt(b); }") == "3"


# ============================================================================
# 3. Integer arithmetic (020-029)
# ============================================================================

def test_020():
    """addition"""
    assert run("void main() { printInt(2 + 3); }") == "5"


def test_021():
    """subtraction"""
    assert run("void main() { printInt(10 - 4); }") == "6"


def test_022():
    """multiplication"""
    assert run("void main() { printInt(6 * 7); }") == "42"


def test_023():
    """integer division truncates"""
    assert run("void main() { printInt(20 / 6); }") == "3"


def test_024():
    """modulo"""
    assert run("void main() { printInt(10 % 3); }") == "1"


def test_025():
    """precedence: * before +"""
    assert run("void main() { printInt(2 + 3 * 4); }") == "14"


def test_026():
    """left associativity of subtraction"""
    assert run("void main() { printInt(10 - 3 - 2); }") == "5"


def test_027():
    """subtraction yields negative result"""
    assert run("void main() { printInt(3 - 10); }") == "-7"


def test_028():
    """division result is zero"""
    assert run("void main() { printInt(3 / 7); }") == "0"


def test_029():
    """compound arithmetic: (8 + 4) / (6 - 4)"""
    assert run("void main() { printInt((8 + 4) / (6 - 4)); }") == "6"


# ============================================================================
# 4. Float arithmetic & int->float coercion (030-039)
# ============================================================================

def test_030():
    """float addition"""
    assert run("void main() { printFloat(1.5 + 2.5); }") == "4.0"


def test_031():
    """float subtraction"""
    assert run("void main() { printFloat(5.5 - 1.25); }") == "4.25"


def test_032():
    """float multiplication"""
    assert run("void main() { printFloat(2.0 * 3.5); }") == "7.0"


def test_033():
    """float division"""
    assert run("void main() { printFloat(5.0 / 2.0); }") == "2.5"


def test_034():
    """int + float coerces int to float"""
    assert run("void main() { printFloat(2 + 0.5); }") == "2.5"


def test_035():
    """float + int coerces int to float"""
    assert run("void main() { printFloat(0.25 + 1); }") == "1.25"


def test_036():
    """int / float yields float division"""
    assert run("void main() { printFloat(1 / 2.0); }") == "0.5"


def test_037():
    """mixed precedence with coercion"""
    assert run("void main() { printFloat(1.0 + 2 * 1.5); }") == "4.0"


def test_038():
    """float variable updated by division"""
    assert run("void main() { float x = 10.0; x = x / 4.0; printFloat(x); }") == "2.5"


def test_039():
    """negate a float expression"""
    assert run("void main() { printFloat(-(1.5 + 2.5)); }") == "-4.0"


# ============================================================================
# 5. Relational operators (040-047)
# ============================================================================

def test_040():
    """less than true"""
    assert run("void main() { if (1 < 2) printInt(1); else printInt(0); }") == "1"


def test_041():
    """less than false"""
    assert run("void main() { if (3 < 2) printInt(1); else printInt(0); }") == "0"


def test_042():
    """less-or-equal at boundary"""
    assert run("void main() { if (5 <= 5) printInt(1); else printInt(0); }") == "1"


def test_043():
    """greater than true"""
    assert run("void main() { if (10 > 3) printInt(1); else printInt(0); }") == "1"


def test_044():
    """greater-or-equal false"""
    assert run("void main() { if (2 >= 7) printInt(1); else printInt(0); }") == "0"


def test_045():
    """equality true"""
    assert run("void main() { if (4 == 4) printInt(1); else printInt(0); }") == "1"


def test_046():
    """inequality true"""
    assert run("void main() { if (4 != 5) printInt(1); else printInt(0); }") == "1"


def test_047():
    """float equality"""
    assert run("void main() { if (1.5 == 1.5) printInt(1); else printInt(0); }") == "1"


# ============================================================================
# 6. Logical operators (048-053)
# ============================================================================

def test_048():
    """logical AND both true"""
    assert run("void main() { if (1 < 2 && 2 < 3) printInt(1); else printInt(0); }") == "1"


def test_049():
    """logical AND one false"""
    assert run("void main() { if (1 < 2 && 5 < 3) printInt(1); else printInt(0); }") == "0"


def test_050():
    """logical OR false/true -> true"""
    assert run("void main() { if (5 < 3 || 1 < 2) printInt(1); else printInt(0); }") == "1"


def test_051():
    """logical OR both false"""
    assert run("void main() { if (5 < 3 || 9 < 3) printInt(1); else printInt(0); }") == "0"


def test_052():
    """logical NOT of true"""
    assert run("void main() { if (!(1 < 2)) printInt(1); else printInt(0); }") == "0"


def test_053():
    """logical NOT of false"""
    assert run("void main() { if (!(5 < 3)) printInt(1); else printInt(0); }") == "1"


# ============================================================================
# 7. Prefix / postfix (054-061)
# ============================================================================

def test_054():
    """prefix ++ returns new value and increments"""
    assert run("void main() { int x = 5; printInt(++x); printInt(x); }") == "66"


def test_055():
    """prefix -- returns new value and decrements"""
    assert run("void main() { int x = 5; printInt(--x); printInt(x); }") == "44"


def test_056():
    """postfix ++ returns old value and increments"""
    assert run("void main() { int x = 5; printInt(x++); printInt(x); }") == "56"


def test_057():
    """postfix -- returns old value and decrements"""
    assert run("void main() { int x = 5; printInt(x--); printInt(x); }") == "54"


def test_058():
    """unary plus has no effect"""
    assert run("void main() { printInt(+9); }") == "9"


def test_059():
    """double negation"""
    assert run("void main() { printInt(-(-12)); }") == "12"


def test_060():
    """double logical not"""
    assert run("void main() { int a = 1; if (!!( a > 0)) printInt(1); else printInt(0); }") == "1"


def test_061():
    """postfix ++ inside arithmetic: 10 + i++ uses old i, then i=2"""
    assert run("void main() { int i = 1; printInt(10 + i++); printInt(i); }") == "112"


# ============================================================================
# 8. If / else (062-069)
# ============================================================================

def test_062():
    """if without else, true branch executes"""
    assert run('void main() { if (1 == 1) printString("T"); }') == "T"


def test_063():
    """if without else, false branch -> nothing printed"""
    assert run('void main() { if (1 == 2) printString("T"); printString("done"); }') == "done"


def test_064():
    """if-else taking else branch"""
    assert run('void main() { if (1 > 2) printString("A"); else printString("B"); }') == "B"


def test_065():
    """nested if"""
    assert run("""
        void main() {
            int x = 10;
            if (x > 0)
                if (x > 5) printString("big");
                else printString("small");
        }
    """) == "big"


def test_066():
    """else-if chain: first branch hits"""
    assert run("""
        void main() {
            int x = 1;
            if (x == 1) printString("one");
            else if (x == 2) printString("two");
            else printString("other");
        }
    """) == "one"


def test_067():
    """else-if chain: middle branch hits"""
    assert run("""
        void main() {
            int x = 2;
            if (x == 1) printString("one");
            else if (x == 2) printString("two");
            else printString("other");
        }
    """) == "two"


def test_068():
    """else-if chain: falls through to final else"""
    assert run("""
        void main() {
            int x = 9;
            if (x == 1) printString("one");
            else if (x == 2) printString("two");
            else printString("other");
        }
    """) == "other"


def test_069():
    """if with compound && condition"""
    assert run("""
        void main() {
            int a = 5; int b = 10;
            if (a > 0 && b > 0) printString("yes");
            else printString("no");
        }
    """) == "yes"


# ============================================================================
# 9. While loops (070-075)
# ============================================================================

def test_070():
    """simple while 0..2"""
    assert run("""
        void main() {
            int i = 0;
            while (i < 3) { printInt(i); i = i + 1; }
        }
    """) == "012"


def test_071():
    """while condition false from start"""
    assert run("""
        void main() {
            while (1 > 2) printString("x");
            printString("done");
        }
    """) == "done"


def test_072():
    """while with break"""
    assert run("""
        void main() {
            int i = 0;
            while (1 == 1) {
                if (i >= 3) break;
                printInt(i);
                i = i + 1;
            }
        }
    """) == "012"


def test_073():
    """while with continue: print only odd numbers"""
    assert run("""
        void main() {
            int i = 0;
            while (i < 6) {
                i = i + 1;
                if (i % 2 == 0) continue;
                printInt(i);
            }
        }
    """) == "135"


def test_074():
    """nested while loops"""
    assert run("""
        void main() {
            int i = 0;
            while (i < 2) {
                int j = 0;
                while (j < 2) { printInt(i); printInt(j); j = j + 1; }
                i = i + 1;
            }
        }
    """) == "00011011"


def test_075():
    """sum 1..10 with while"""
    assert run("""
        void main() {
            int i = 1; int s = 0;
            while (i <= 10) { s = s + i; i = i + 1; }
            printInt(s);
        }
    """) == "55"


# ============================================================================
# 10. For loops (076-083)
# ============================================================================

def test_076():
    """standard for 0..4"""
    assert run("""
        void main() {
            for (int i = 0; i < 5; i++) printInt(i);
        }
    """) == "01234"


def test_077():
    """for counting down"""
    assert run("""
        void main() {
            for (int i = 3; i > 0; i--) printInt(i);
        }
    """) == "321"


def test_078():
    """for with break"""
    assert run("""
        void main() {
            for (int i = 0; i < 10; i++) {
                if (i == 3) break;
                printInt(i);
            }
        }
    """) == "012"


def test_079():
    """for with continue: print only even i"""
    assert run("""
        void main() {
            for (int i = 0; i < 6; i++) {
                if (i % 2 != 0) continue;
                printInt(i);
            }
        }
    """) == "024"


def test_080():
    """nested for: 2x2 index pairs"""
    assert run("""
        void main() {
            for (int i = 0; i < 2; i++)
                for (int j = 0; j < 2; j++) {
                    printInt(i); printInt(j);
                }
        }
    """) == "00011011"


def test_081():
    """for with multiply update"""
    assert run("""
        void main() {
            for (int i = 1; i <= 16; i = i * 2) printInt(i);
        }
    """) == "124816"


def test_082():
    """for computing factorial of 5"""
    assert run("""
        void main() {
            int r = 1;
            for (int i = 1; i <= 5; i++) r = r * i;
            printInt(r);
        }
    """) == "120"


def test_083():
    """for init variable accessible after loop"""
    assert run("""
        void main() {
            for (int i = 0; i < 4; i++) {}
            printInt(i);
        }
    """) == "4"


# ============================================================================
# 11. Switch (084-088)
# ============================================================================

def test_084():
    """switch matches a case"""
    assert run("""
        void main() {
            int x = 2;
            switch (x) {
                case 1: printString("one"); break;
                case 2: printString("two"); break;
                case 3: printString("three"); break;
                default: printString("d");
            }
        }
    """) == "two"


def test_085():
    """switch falls to default"""
    assert run("""
        void main() {
            int x = 99;
            switch (x) {
                case 1: printString("one"); break;
                default: printString("other");
            }
        }
    """) == "other"


def test_086():
    """switch fall-through without break"""
    assert run("""
        void main() {
            int x = 1;
            switch (x) {
                case 1: printString("A");
                case 2: printString("B"); break;
                case 3: printString("C"); break;
            }
        }
    """) == "AB"


def test_087():
    """switch no default, no match -> nothing printed before 'end'"""
    assert run("""
        void main() {
            int x = 5;
            switch (x) {
                case 1: printString("one"); break;
            }
            printString("end");
        }
    """) == "end"


def test_088():
    """switch break exits switch but not enclosing for"""
    assert run("""
        void main() {
            for (int i = 0; i < 3; i++) {
                switch (i) {
                    case 0: printString("a"); break;
                    case 1: printString("b"); break;
                    default: printString("d");
                }
            }
        }
    """) == "abd"


# ============================================================================
# 12. Functions (089-096)
# ============================================================================

def test_089():
    """void function call"""
    assert run("""
        void greet() { printString("hi"); }
        void main() { greet(); }
    """) == "hi"


def test_090():
    """int function with params"""
    assert run("""
        int add(int a, int b) { return a + b; }
        void main() { printInt(add(20, 22)); }
    """) == "42"


def test_091():
    """float function"""
    assert run("""
        float half(float x) { return x / 2.0; }
        void main() { printFloat(half(5.0)); }
    """) == "2.5"


def test_092():
    """recursion: factorial"""
    assert run("""
        int fact(int n) {
            if (n <= 1) return 1;
            return n * fact(n - 1);
        }
        void main() { printInt(fact(6)); }
    """) == "720"


def test_093():
    """recursion: fibonacci"""
    assert run("""
        int fib(int n) {
            if (n < 2) return n;
            return fib(n - 1) + fib(n - 2);
        }
        void main() { printInt(fib(10)); }
    """) == "55"


def test_094():
    """two functions calling each other"""
    assert run("""
        int dbl(int n) { return n * 2; }
        int quad(int n) { return dbl(dbl(n)); }
        void main() { printInt(quad(3)); }
    """) == "12"


def test_095():
    """function returns string"""
    assert run("""
        string greet() { return "hello"; }
        void main() { printString(greet()); }
    """) == "hello"


def test_096():
    """void function with early return skips rest"""
    assert run("""
        void maybe(int n) {
            if (n < 0) return;
            printInt(n);
        }
        void main() { maybe(1); maybe(-2); maybe(3); }
    """) == "13"


# ============================================================================
# 13. Structs (097-104)
# ============================================================================

def test_097():
    """simple struct literal + print members"""
    assert run("""
        struct Point { int x; int y; };
        void main() {
            Point p = {3, 4};
            printInt(p.x);
            printInt(p.y);
        }
    """) == "34"


def test_098():
    """struct member sum"""
    assert run("""
        struct Point { int x; int y; };
        void main() {
            Point p = {3, 4};
            printInt(p.x + p.y);
        }
    """) == "7"


def test_099():
    """struct member write"""
    assert run("""
        struct Box { int v; };
        void main() {
            Box b = {10};
            b.v = 99;
            printInt(b.v);
        }
    """) == "99"


def test_100():
    """struct with float and string fields"""
    assert run("""
        struct Rec { float f; string s; };
        void main() {
            Rec r = {1.5, "hi"};
            printFloat(r.f);
            printString(r.s);
        }
    """) == "1.5hi"


def test_101():
    """nested struct literal"""
    assert run("""
        struct Inner { int v; };
        struct Outer { Inner a; int b; };
        void main() {
            Outer o = {{7}, 8};
            printInt(o.a.v);
            printInt(o.b);
        }
    """) == "78"


def test_102():
    """struct as function parameter"""
    assert run("""
        struct Point { int x; int y; };
        int sum(Point p) { return p.x + p.y; }
        void main() {
            Point p = {10, 20};
            printInt(sum(p));
        }
    """) == "30"


def test_103():
    """struct as function return value"""
    assert run("""
        struct Pair { int a; int b; };
        Pair mk() { return {5, 6}; }
        void main() {
            Pair p = mk();
            printInt(p.a);
            printInt(p.b);
        }
    """) == "56"


def test_104():
    """modify nested struct field"""
    assert run("""
        struct Inner { int v; };
        struct Outer { Inner i; };
        void main() {
            Outer o = {{1}};
            o.i.v = 42;
            printInt(o.i.v);
        }
    """) == "42"


# ============================================================================
# 14. I/O built-ins (105-110)
# ============================================================================

def test_105():
    """readInt -> printInt"""
    assert run("void main() { int x = readInt(); printInt(x); }", "123") == "123"


def test_106():
    """readInt used in arithmetic"""
    assert run("void main() { int x = readInt(); printInt(x * 2); }", "21") == "42"


def test_107():
    """readFloat -> printFloat"""
    assert run("void main() { float x = readFloat(); printFloat(x); }", "3.5") == "3.5"


def test_108():
    """readString -> printString"""
    assert run('void main() { string s = readString(); printString(s); }', "hello") == "hello"


def test_109():
    """read two ints and print their sum"""
    assert run("void main() { int a = readInt(); int b = readInt(); printInt(a + b); }", "10 32") == "42"


def test_110():
    """read int then branch on value"""
    assert run("""
        void main() {
            int n = readInt();
            if (n > 0) printString("pos");
            else printString("nonpos");
        }
    """, "5") == "pos"


# ============================================================================
# 15. Edge cases & complex scenarios (111-119)
# ============================================================================

def test_111():
    """variable shadowing in inner block"""
    assert run("""
        void main() {
            int x = 1;
            { int x = 99; printInt(x); }
            printInt(x);
        }
    """) == "991"


def test_112():
    """empty block does nothing"""
    assert run("""
        void main() {
            printString("before");
            {}
            printString("after");
        }
    """) == "beforeafter"


def test_113():
    """early return inside conditional branch"""
    assert run("""
        int choose(int n) {
            if (n > 0) return 1;
            return -1;
        }
        void main() {
            printInt(choose(5));
            printInt(choose(-3));
        }
    """) == "1-1"


def test_114():
    """compound boolean: (a>0) && (b>0 || c>0)"""
    assert run("""
        void main() {
            int a = 1; int b = 0; int c = 2;
            if (a > 0 && (b > 0 || c > 0)) printInt(1);
            else printInt(0);
        }
    """) == "1"


def test_115():
    """compute average of 1..5 with for"""
    assert run("""
        void main() {
            int s = 0; int n = 5;
            for (int i = 1; i <= n; i++) s = s + i;
            printInt(s / n);
        }
    """) == "3"


def test_116():
    """boundary: INT_MAX - 1 + 1"""
    assert run("void main() { printInt(2147483646 + 1); }") == "2147483647"


def test_117():
    """prefix ++ on struct member"""
    assert run("""
        struct C { int x; };
        void main() {
            C c = {10};
            printInt(++c.x);
            printInt(c.x);
        }
    """) == "1111"


def test_118():
    """postfix ++ on struct member"""
    assert run("""
        struct C { int x; };
        void main() {
            C c = {10};
            printInt(c.x++);
            printInt(c.x);
        }
    """) == "1011"


def test_119():
    """FizzBuzz 1..15"""
    assert run("""
        void main() {
            for (int i = 1; i <= 15; i++) {
                int m3 = i % 3;
                int m5 = i % 5;
                if (m3 == 0 && m5 == 0) printString("FB");
                else if (m3 == 0) printString("F");
                else if (m5 == 0) printString("B");
                else printInt(i);
            }
        }
    """) == "12F4BF78FB11F1314FB"

def test_120():
    assert run("""
        void main() {
            printInt(1 <= 1.2);
        }
    """) == "1"

def test_121():
    source = """
    int foo() {
        printInt(1);
        return 1;
    }
    void main() {
        printInt(1 && foo());
        printInt(1 || foo());
    }
    """
    assert run(source) == "111"

def test_122():
    source = """
    struct Point {
        int x;
        int y;
    };
    void main(){
        Point p;
        p.x = 2;
        printInt(p.x);
    }
    """
    assert run(source) == "2"

def test_123():
    source = """
    void main(){
        int a;
        float b;
        string c;
        printInt(a);
        printFloat(b);
        printString(c);
    }
    """
    assert run(source) == "00.0"

def test_124():
    source = """
    struct Point {
        int x;
        float y;
        string z;
    };
    void main(){
        Point p;
        printInt(p.x);
        printFloat(p.y);
        printString(p.z);
    }
    """
    assert run(source) == "00.0"

def test_125():
    source = """
    foo(int a, int b) {return a + b;}
    void main(){
        auto a; auto b;
        printInt(foo(a, b));
    }
    """
    assert run(source) == "0"

def test_126():
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
    assert run(source, "4\n0.2\nvotien\n1\n0.5") == "4.2Hello, votien"

def test_127():
    source = """
    int factorial(int n) {
        if (n <= 1) {
            return 1;
        } else {
            return n * factorial(n - 1);
        }
    }

    void main() {
        auto num = 10;
        auto result = factorial(num);
        printInt(result);
    }
    """
    assert run(source) == "3628800"

def test_128():
    source = """
    int foo(int n){
        if (n <= 1){
            printInt(1);
            return 1;
        }
        else{
            printInt(2);
            return 2;
        }
    }
    void main(){
        printInt(foo(1));
        printInt(foo(2));
    }
    """
    assert run(source) == "1122"

def test_129():
    source = """
    void main() {
        int i = 2;
        switch (i) {
            default: int i = 3;
        }
        printInt(i);
    }
    """
    assert run(source) == "2"

def test_130():
    """struct declared without initializer, then member assigned"""
    assert run("""
        struct Point { int x; int y; };
        void main() {
            Point p;
            p.x = 2;
            printInt(p.x);
        }
    """) == "2"


def test_131():
    """primitive vars declared without initializer default to 0/0.0/empty-string"""
    assert run("""
        void main() {
            int a;
            float b;
            string c;
            printInt(a);
            printFloat(b);
            printString(c);
        }
    """) == "00.0"


def test_132():
    """struct fields without initializer default to 0/0.0/empty-string (not null)"""
    assert run("""
        struct Point { int x; float y; string z; };
        void main() {
            Point p;
            printInt(p.x);
            printFloat(p.y);
            printString(p.z);
        }
    """) == "00.0"


def test_133():
    """nested struct field without initializer is auto-initialized (not null)"""
    assert run("""
        struct A { int x; };
        struct B { A a; };
        void main() {
            B p;
            printInt(p.a.x + 1);
        }
    """) == "1"


def test_134():
    """auto var without init defaults to int, supports chained assignment"""
    assert run("""
        void main() {
            auto a; auto b;
            { a = b = 1; }
            printInt(a + b);
        }
    """) == "2"


def test_135():
    """function without explicit return type inferred as int"""
    assert run("""
        foo(int a, int b) { return a + b; }
        void main() {
            auto a; auto b;
            printInt(foo(a, b));
        }
    """) == "0"


def test_136():
    """auto var without init (IntType default) promoted to FloatType on first float assignment"""
    assert run("""
        void main() {
            auto x = readInt();
            auto y = readFloat();
            auto name = readString();
            auto sum;
            sum = x + y;
            int count = 0;
            float total = 0.0;
            string greeting = "Hello, ";
            int i;
            float f;
            i = readInt();
            f = readFloat();
            printFloat(sum);
            printString(greeting);
            printString(name);
        }
    """, "2 2.2 votien 0 0.0") == "4.2Hello, votien"


def test_137():
    """recursive function with if-else both returning (no goto after then-return)"""
    assert run("""
        int factorial(int n) {
            if (n <= 1) {
                return 1;
            } else {
                return n * factorial(n - 1);
            }
        }
        void main() {
            auto num = 10;
            auto result = factorial(num);
            printInt(result);
        }
    """) == "3628800"


def test_138():
    """switch with continue (jumps to enclosing while) and break (exits switch)"""
    assert run("""
        void main() {
            int i = 0;
            while (i < 5) {
            i = i + 1;
                switch (i) {
                    case 2: continue;
                    case 4: break;
                    default: printInt(i);
                }
                printInt(i);
            }
        }
    """) == "1133455"


def test_139():
    """var declared inside switch case/default must not leak into outer scope"""
    assert run("""
        void main() {
            int i = 2;
            switch (i) {
                default: int i = 3;
            }
            printInt(i);
        }
    """) == "2"


def test_140():
    """switch fall-through: var declared in case 5 is visible in default (shared scope)"""
    assert run("""
        void main() {
            int x = 5;
            switch (x) {
                case 1: printInt(1);
                case 3: printInt(3);
                case 5: int b = 2; printInt(b);
                default: b = 3; printInt(b);
            }
        }
    """) == "23"

def test_141():
    assert run("""
    void main(){
        int x = 5;
        switch(x){
            case (1+0): printInt(1); break;
            case (1+2): printInt(3); break;
            case (1+4): printInt(5); break;
            default: printInt(0); break;
        }
    }
    """) == "5"

def test_142():
    source = """
    void main(){
        printString("ccc\\nccc");
    }
    """
    assert run(source) == "ccc\nccc"

def test_143():
    source = """
    struct Point {
        int x;
        int y;
    };

    void main() {
        Point p1;
        Point p2;

        p2.x = 10;
        p2.y = 20;

        p1 = p2;   // copy struct

        p2.x = 99;
        p2.y = 88;

        printInt(p1.x);
        printInt(p1.y);
        printInt(p2.x);
        printInt(p2.y);
    }
    """
    assert run(source) == "10209988"

def test_144():
    source = """
    struct Point {
        int x;
        int y;
        int c;
        int d;
    };
    void main(){
        Point p;
        p.d = 2;
        Point p1 = p;
        p1.d = 3;
        printInt(p.d);
    }
    """
    assert run(source) == "2"

def test_145():
    source = """
    struct Point {
        int x;
    };

    void change(Point p){
        p.x = 99;
    }

    void main(){
        Point a;
        a.x = 10;

        change(a);

        printInt(a.x);
    }
    """
    assert run(source) == "10"

def test_146():
    assert run("""
    struct C {
        int x;
    };

    struct A {
        C x;
    };

    struct B {
        A a;
    };

    void main() {
        B b;
        b.a.x.x = 5;
        printInt(++b.a.x.x);
    }
    """) == "6"

def test_147():
    source = """
    foo(int a, float b){
        return a + b;
    }
    void main(){
        printInt(5.0 > foo(1,2.3));
    }
    """
    assert run(source) == "1"

def test_148():
    source = """
    void main() {
        int i = 2;
        switch (i) {
            default: int i = 3;
        }
        printInt(i);
    }
    """
    assert run(source) == "2"

def test_149():
    source = """
    foo(int a, float b){
            return a + b;
    }
    void main(){
        auto x = foo(1, 2.5);
        int g = x < 1.5;
        printInt(g);
        switch(g){
            case 0:
                printFloat(0.0);
        }
    }
    """
    assert run(source) == "00.0"

def test_150():
    assert run("""
    struct Pair { int x; int y; };

    Pair make(int a, int b) {
        Pair p = {a, b};
        return p;
    }

    void main() {
        Pair p = make(8, 9);
        printInt(p.x * p.y);
    }
    """) == "72"

def test_151():
    source = """
    struct Inner {
        int val;
    };
    struct Outer {
        Inner inner;
        int extra;
    };
    void main(){
        Outer o = {{5}, 10};
        printInt(o.inner.val + o.extra);
    }
    """
    assert run(source) == "15"



if __name__ == "__main__":
    import pytest

    if len(sys.argv) > 1:
        test_ids = [f"{__file__}::test_{int(n):03d}" for n in sys.argv[1:]]
        sys.exit(pytest.main(["-v"] + test_ids))
    else:
        sys.exit(pytest.main(["-v", __file__]))
