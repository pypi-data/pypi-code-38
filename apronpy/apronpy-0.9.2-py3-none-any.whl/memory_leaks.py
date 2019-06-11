from copy import deepcopy

from apronpy.coeff import PyMPQScalarCoeff
from apronpy.environment import PyEnvironment
from apronpy.lincons0 import ConsTyp
from apronpy.polka import PyPolkaMPQstrict
from apronpy.t1p import PyT1pMPQ
from apronpy.tcons1 import PyTcons1, PyTcons1Array
from apronpy.texpr0 import TexprOp, TexprRtype, TexprRdir
from apronpy.texpr1 import PyTexpr1
from apronpy.var import PyVar


def do():
    size = 1#000000

    for i in range(size):

        x = PyVar('x')
        y = PyVar('y')
        r_vars = [x, y]
        for i in range(10, 52):
            name = 'x{}'.format(i)
            r_vars.append(PyVar(name))
        e = PyEnvironment([], r_vars)
        p0 = [PyT1pMPQ(e)]

        # o1 = PyVar('o1')
        # o2 = PyVar('o2')
        # h1 = PyVar('h1')
        # h2 = PyVar('h2')
        # h3 = PyVar('h3')
        # h4 = PyVar('h4')
        # h5 = PyVar('h5')
        # h6 = PyVar('h6')
        # h7 = PyVar('h7')
        # h8 = PyVar('h8')
        # h9 = PyVar('h9')
        # e = PyEnvironment([], [o1, o2, h1, h2, h3, h4, h5, h6, h7, h8, h9])
        #
        #
        o01 = PyTexpr1.var(e, PyVar('x'))
        o02 = PyTexpr1.cst(e, PyMPQScalarCoeff(0))
        x0 = PyTexpr1.binop(TexprOp.AP_TEXPR_SUB, o02, o01, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        c0 = PyTcons1.make(x0, ConsTyp.AP_CONS_SUP)     # o2 - o1 > 0
        a0 = PyTcons1Array([c0])
        p1 = [deepcopy(p).meet(a0) for p in p0]
        print(p1)

        # x1a = PyTexpr1.var(e, PyVar('o1'))
        # p2a = [deepcopy(p).substitute(PyVar('o1'), x1a) for p in p1]     # o1 = o1
        # o1a = PyTexpr1.var(e, PyVar('o1'))
        # c1a = PyTcons1.make(o1a, ConsTyp.AP_CONS_SUPEQ)     # o1 >= 0
        # a1a = PyTcons1Array([c1a])
        # p3a = [deepcopy(p).meet(a1a) for p in p2a]
        # #
        # x1b = PyTexpr1.cst(e, PyMPQScalarCoeff(0.0))
        # p2b = [deepcopy(p).substitute(PyVar('o1'), x1b) for p in p1]     # o1 = 0
        # o2b = PyTexpr1.var(e, PyVar('o2'))
        # k2b = PyTexpr1.cst(e, PyMPQScalarCoeff(-1.0))
        # t2b = PyTexpr1.binop(TexprOp.AP_TEXPR_MUL, k2b, o2b, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # c1b = PyTcons1.make(t2b, ConsTyp.AP_CONS_SUP)
        # a1b = PyTcons1Array([c1b])
        # p3b = [deepcopy(p).meet(a1b) for p in p2b]
        # #
        # p3 = p3a + p3b
        #
        # h21 = PyTexpr1.var(e, PyVar('h1'))
        # h22 = PyTexpr1.var(e, PyVar('h2'))
        # h23 = PyTexpr1.var(e, PyVar('h3'))
        # h24 = PyTexpr1.var(e, PyVar('h4'))
        # h25 = PyTexpr1.var(e, PyVar('h5'))
        # h26 = PyTexpr1.var(e, PyVar('h6'))
        # h27 = PyTexpr1.var(e, PyVar('h7'))
        # h28 = PyTexpr1.var(e, PyVar('h8'))
        # h29 = PyTexpr1.var(e, PyVar('h9'))
        # k20 = PyTexpr1.cst(e, PyMPQScalarCoeff(-0.2))
        # t20 = PyTexpr1.binop(TexprOp.AP_TEXPR_MUL, k20, h21, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # k21 = PyTexpr1.cst(e, PyMPQScalarCoeff(0.3))
        # t21 = PyTexpr1.binop(TexprOp.AP_TEXPR_MUL, k21, h22, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # k22 = PyTexpr1.cst(e, PyMPQScalarCoeff(-0.1))
        # t22 = PyTexpr1.binop(TexprOp.AP_TEXPR_MUL, k22, h23, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # k23 = PyTexpr1.cst(e, PyMPQScalarCoeff(0.2))
        # t23 = PyTexpr1.binop(TexprOp.AP_TEXPR_MUL, k23, h24, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # k24 = PyTexpr1.cst(e, PyMPQScalarCoeff(0.1))
        # t24 = PyTexpr1.binop(TexprOp.AP_TEXPR_MUL, k24, h25, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # k25 = PyTexpr1.cst(e, PyMPQScalarCoeff(0.3))
        # t25 = PyTexpr1.binop(TexprOp.AP_TEXPR_MUL, k25, h26, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # k26 = PyTexpr1.cst(e, PyMPQScalarCoeff(0.4))
        # t26 = PyTexpr1.binop(TexprOp.AP_TEXPR_MUL, k26, h27, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # k27 = PyTexpr1.cst(e, PyMPQScalarCoeff(0.2))
        # t27 = PyTexpr1.binop(TexprOp.AP_TEXPR_MUL, k27, h28, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # k28 = PyTexpr1.cst(e, PyMPQScalarCoeff(-0.1))
        # t28 = PyTexpr1.binop(TexprOp.AP_TEXPR_MUL, k28, h29, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # k29 = PyTexpr1.cst(e, PyMPQScalarCoeff(0.4))
        # x20 = PyTexpr1.binop(TexprOp.AP_TEXPR_ADD, t20, t21, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # x21 = PyTexpr1.binop(TexprOp.AP_TEXPR_ADD, x20, t22, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # x22 = PyTexpr1.binop(TexprOp.AP_TEXPR_ADD, x21, t23, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # x23 = PyTexpr1.binop(TexprOp.AP_TEXPR_ADD, x22, t24, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # x24 = PyTexpr1.binop(TexprOp.AP_TEXPR_ADD, x23, t25, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # x25 = PyTexpr1.binop(TexprOp.AP_TEXPR_ADD, x24, t26, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # x26 = PyTexpr1.binop(TexprOp.AP_TEXPR_ADD, x25, t27, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # x27 = PyTexpr1.binop(TexprOp.AP_TEXPR_ADD, x26, t28, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # x28 = PyTexpr1.binop(TexprOp.AP_TEXPR_ADD, x27, k29, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # # r = repr(x28)
        # p4 = [deepcopy(p).substitute(PyVar('o2'), x28) for p in p3]
        #
        # h31 = PyTexpr1.var(e, PyVar('h1'))
        # h32 = PyTexpr1.var(e, PyVar('h3'))
        # h33 = PyTexpr1.var(e, PyVar('h3'))
        # h34 = PyTexpr1.var(e, PyVar('h4'))
        # h35 = PyTexpr1.var(e, PyVar('h5'))
        # h36 = PyTexpr1.var(e, PyVar('h6'))
        # h37 = PyTexpr1.var(e, PyVar('h7'))
        # h38 = PyTexpr1.var(e, PyVar('h8'))
        # h39 = PyTexpr1.var(e, PyVar('h9'))
        # k30 = PyTexpr1.cst(e, PyMPQScalarCoeff(0.4))
        # t30 = PyTexpr1.binop(TexprOp.AP_TEXPR_MUL, k30, h31, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # k31 = PyTexpr1.cst(e, PyMPQScalarCoeff(-0.1))
        # t31 = PyTexpr1.binop(TexprOp.AP_TEXPR_MUL, k31, h32, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # k32 = PyTexpr1.cst(e, PyMPQScalarCoeff(0.2))
        # t32 = PyTexpr1.binop(TexprOp.AP_TEXPR_MUL, k32, h33, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # k33 = PyTexpr1.cst(e, PyMPQScalarCoeff(0.3))
        # t33 = PyTexpr1.binop(TexprOp.AP_TEXPR_MUL, k33, h34, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # k34 = PyTexpr1.cst(e, PyMPQScalarCoeff(-0.1))
        # t34 = PyTexpr1.binop(TexprOp.AP_TEXPR_MUL, k34, h35, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # k35 = PyTexpr1.cst(e, PyMPQScalarCoeff(-0.2))
        # t35 = PyTexpr1.binop(TexprOp.AP_TEXPR_MUL, k35, h36, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # k36 = PyTexpr1.cst(e, PyMPQScalarCoeff(0.4))
        # t36 = PyTexpr1.binop(TexprOp.AP_TEXPR_MUL, k36, h37, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # k37 = PyTexpr1.cst(e, PyMPQScalarCoeff(0.3))
        # t37 = PyTexpr1.binop(TexprOp.AP_TEXPR_MUL, k37, h38, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # k38 = PyTexpr1.cst(e, PyMPQScalarCoeff(0.1))
        # t38 = PyTexpr1.binop(TexprOp.AP_TEXPR_MUL, k38, h39, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # k39 = PyTexpr1.cst(e, PyMPQScalarCoeff(0.4))
        # x30 = PyTexpr1.binop(TexprOp.AP_TEXPR_ADD, t30, t31, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # x31 = PyTexpr1.binop(TexprOp.AP_TEXPR_ADD, x30, t32, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # x32 = PyTexpr1.binop(TexprOp.AP_TEXPR_ADD, x31, t33, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # x33 = PyTexpr1.binop(TexprOp.AP_TEXPR_ADD, x32, t34, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # x34 = PyTexpr1.binop(TexprOp.AP_TEXPR_ADD, x33, t35, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # x35 = PyTexpr1.binop(TexprOp.AP_TEXPR_ADD, x34, t36, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # x36 = PyTexpr1.binop(TexprOp.AP_TEXPR_ADD, x35, t37, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # x37 = PyTexpr1.binop(TexprOp.AP_TEXPR_ADD, x36, t38, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # x38 = PyTexpr1.binop(TexprOp.AP_TEXPR_ADD, x37, k39, TexprRtype.AP_RTYPE_DOUBLE, TexprRdir.AP_RDIR_RND)
        # p5 = [deepcopy(p).substitute(PyVar('o1'), x38) for p in p4]
        # print(p5)


do()
