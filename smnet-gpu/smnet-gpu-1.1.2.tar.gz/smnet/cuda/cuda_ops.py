# --------------------------------------------------------
# SMNet gpu math ops
# Licensed under The MIT License [see LICENSE for details]
# Copyright 2019 smarsu. All Rights Reserved.
# --------------------------------------------------------

"""Basic mathematical operations based on gpu.
"""

import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule

mod = SourceModule("""
#define MAX_SHAPE_SIZE 8


// Zeros
__global__ void zeros(float *a)
{
    int idx = blockIdx.x;
    a[idx] = 0;
}


// Full
__global__ void full(float *a, float *value)
{
    int idx = blockIdx.x;
    a[idx] = *value;
}


// Matmul
__global__ void matmul(float *a, float *b, float *c,
                       int *attrs)
{
    /* Matrix multiplication
    
    Inputs:
        a: shape [n, k]
        b: shape [k, m]
    Outputs:
        c: shape [n, m]
    Attrs:
        attrs: [c_size, m, k]
    */

    // Cause we set grid to n * m, and block to 1.
    int c_size = attrs[0], 
        m = attrs[1], 
        k = attrs[2];
    int idx = blockIdx.x;
    if (idx < c_size) {
        int row = idx / m;
        int col = idx % m;

        int row_ind = row * k;
        float tmp = 0;
        for (int i = 0; i < k; i++) {
            tmp += a[row_ind + i] * b[m * i + col];
        }
        c[idx] = tmp;
    }
}


// Transpose
__global__ void transpose(float *a, float *output, 
                          int *perm, int *src_shape, int *shape_size_)
{
    /* Transpose operate

    dst(i, j) = src(j, i)

    Input:
        a: shape ?
    Output:
        output: shape ?
    Attrs:
        perm: list of int
        src_shape: list of int
    */

    int idx = blockIdx.x;
    int tmp_idx = idx;
    int old_idns[MAX_SHAPE_SIZE];

    int shape_size = shape_size_[0];
    for (int i = shape_size - 1; i >= 0; i--) {
        old_idns[i] = idx % src_shape[i];
        idx /= src_shape[i];
    }
    int tmp = 0, factor = 1;
    for (int i = shape_size - 1; i >= 0; i--) {
        tmp += factor * old_idns[perm[i]];
        factor *= src_shape[perm[i]];
    }
    output[tmp] = a[tmp_idx];
}


// Add
__global__ void add(float *a, float *b, float *c,
                    int *pad_shape_a, int *pad_shape_b, int *broadcast_shape,
                    int *shape_size_)
{
    int idx = blockIdx.x;
    int tmp_idx = idx;
    int shape_size = shape_size_[0];

    int cur_a_shape[MAX_SHAPE_SIZE];
    int cur_b_shape[MAX_SHAPE_SIZE];
    for (int i = shape_size - 1; i >= 0; i--) {
        int remainder = idx % broadcast_shape[i];
        if (pad_shape_a[i] == 1) {
            cur_a_shape[i] = 0;
        }
        else {
            cur_a_shape[i] = remainder;
        }

        if (pad_shape_b[i] == 1) {
            cur_b_shape[i] = 0;
        }
        else {
            cur_b_shape[i] = remainder;
        }
        idx /= broadcast_shape[i];
    }
    int a_ind = 0, factor_a = 1;
    for (int i = shape_size - 1; i >= 0; i--) {
        a_ind += factor_a * cur_a_shape[i];
        factor_a *= pad_shape_a[i];
    }
    int b_ind = 0, factor_b = 1;
    for (int i = shape_size - 1; i >= 0; i--) {
        b_ind += factor_b * cur_b_shape[i];
        factor_b *= pad_shape_b[i];
    }
    c[tmp_idx] = a[a_ind] + b[b_ind];
}


// AddGrad
__global__ void add_grad(float *a, float *grad, 
                         int *grad_shape, int *a_pad_shape, int *shape_size)
{
    int idx = blockIdx.x;
    int tmp_idx = idx;

    int a_shape[MAX_SHAPE_SIZE];
    for (int i = *shape_size - 1; i >= 0; i--) {
        if (a_pad_shape[i] == 1) {
            a_shape[i] = 0;
        }
        else {
            a_shape[i] = idx % grad_shape[i];
        }
        idx /= grad_shape[i];
    }
    int a_ind = 0, factor = 1;
    for (int i = *shape_size - 1; i >= 0; i--) {
        a_ind += factor * a_shape[i];
        factor *= a_pad_shape[i];
    }
    a[a_ind] += grad[tmp_idx];
}


// BiasAdd
__global__ void bias_add(float *value, float *bias, float *output, int *bias_size) 
{
    int idx = blockIdx.x;
    output[idx] = value[idx] + bias[idx % bias_size[0]];
}


// IdentityAdd
__global__ void identity_add(float *a, float *b, float *c) 
{
    /*
    Raise:
        ShapeError: If inputs don't have same shape.
    */
    int idx = blockIdx.x;
    c[idx] = a[idx] + b[idx];
}


// LeftAdd
__global__ void left_add(float *a, float *b) 
{
    int idx = blockIdx.x;
    a[idx] += b[idx];
}


// LeftSubtract
__global__ void left_subtract(float *a, float *b)
{
    int idx = blockIdx.x;
    a[idx] -= b[idx];
}


// Relu
__global__ void relu(float *input, float *output)
{
    int idx = blockIdx.x;
    if (input[idx] > 0) {
        output[idx] = input[idx];
    }
    else {
        output[idx] = 0;
    }
}


// ReluGrad
__global__ void relu_grad(float *x_grad, float *grad, 
                          float *x)
{
    int idx = blockIdx.x;
    if (x[idx] > 0) {
        x_grad[idx] += grad[idx];
    }
}


// Half square error
__global__ void hse(float *a, float *b, float *c) 
{
    int idx = blockIdx.x;
    float sub = a[idx] - b[idx];
    c[idx] = 0.5 * sub * sub;
}


// HseGrad
__global__ void hse_grad(float *a_grad, float *a, float *b, float *grad)
{
    int idx = blockIdx.x;
    a_grad[idx] += grad[idx] * (a[idx] - b[idx]);
}
""")


matmul = mod.get_function('matmul')
transpose = mod.get_function('transpose')
add = mod.get_function('add')
add_grad = mod.get_function('add_grad')
bias_add = mod.get_function('bias_add')
add_i = mod.get_function('identity_add')
relu = mod.get_function('relu')
relu_grad = mod.get_function('relu_grad')
hse = mod.get_function('hse')
hse_grad = mod.get_function('hse_grad')
zeros = mod.get_function('zeros')
full = mod.get_function('full')
left_add = mod.get_function('left_add')
left_subtract = mod.get_function('left_subtract')
