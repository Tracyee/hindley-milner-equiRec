# hindley-milner-equiRec

This project implements a Hindley Milner based type inference system with equi-recursive types.


## The Language

The language that is dealt with in this project is a simple typed λ -calculus with constants. This can be interpreted as a generalization of Simply typed lambda calculus ([STLC](https://en.wikipedia.org/wiki/Simply_typed_lambda_calculus)), with an addition of let expressions.

### Syntax

<img src="https://render.githubusercontent.com/render/math?math=e::=x\mid \lambda x.e\mid e\  e\,\mid \text{let}\  x = e\  \text{in}\  e\mid c">


## The Type Environment

The initial type environment contains the following primitives &mdash; booleans, integers, pairs, fst, snd, inr, inl, match, unit, unitCase, fix point combinator, conditionals, zero, pred, and times. The following are their corresponding types.

| Primitives     |                                                                                    Type                                                                                     |
| -------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| `true, false`  |                                                                                    bool                                                                                     |
| `1, 2, 3, ...` |                                                                                     int                                                                                     |
| `pair`         |                      <img src="https://render.githubusercontent.com/render/math?math=\forall \alpha \beta. \alpha \to \beta \to \alpha \times \beta">                       |
| `fst`          |                            <img src="https://render.githubusercontent.com/render/math?math=\forall \alpha \beta. \alpha \times \beta\to \alpha">                            |
| `snd`          |                            <img src="https://render.githubusercontent.com/render/math?math=\forall \alpha \beta. \alpha \times \beta\to \beta">                             |
| `inr`          |                              <img src="https://render.githubusercontent.com/render/math?math=\forall \alpha \beta. \beta\to \alpha %2B \beta">                              |
| `inl`          |                             <img src="https://render.githubusercontent.com/render/math?math=\forall \alpha \beta. \alpha\to \alpha %2B \beta">                              |
| `match`        | <img src="https://render.githubusercontent.com/render/math?math=\forall \alpha \beta \gamma. (\alpha %2B \beta) \to (\alpha \to \gamma) \to (\beta \to \gamma) \to \gamma"> |
| `unit`         |                                                                                    unit                                                                                     |
| `unitCase`     |                                       <img src="https://render.githubusercontent.com/render/math?math=\forall \alpha. 1 \to \alpha">                                        |
| `fix`          |           <img src="https://render.githubusercontent.com/render/math?math=\forall \alpha \beta. ((\alpha \to \beta) \to \alpha \to \beta) \to \alpha \to \beta">            |
| `cond`         |                       <img src="https://render.githubusercontent.com/render/math?math=\forall \alpha. \text{bool} \to \alpha \to \alpha \to \alpha">                        |
| `pred`         |                                         <img src="https://render.githubusercontent.com/render/math?math=\text{int}\to \text{int}">                                          |
| `zero`         |                                         <img src="https://render.githubusercontent.com/render/math?math=\text{int}\to \text{bool}">                                         |
| `times`        |                                  <img src="https://render.githubusercontent.com/render/math?math=\text{int}\to \text{int}\to \text{int}">                                   |

Among the above primitives, `true, fals`, `1, 2, 3, ...` and `unit` are basic types.

`pair`, `fst` and `snd` are provided for constructing and decomposing [Product Type](https://en.wikipedia.org/wiki/Product_type).

`inl`, `inr` and `match` are provided for constructing and decomposing [Sum Type](https://en.wikipedia.org/wiki/Tagged_union). 

`unit`, and `unitCase` are provided for constructing and decomposing [Unit Type](https://en.wikipedia.org/wiki/Unit_type). 

With sum type, product type and unit type, we can construct [equirecursive types](https://en.wikipedia.org/wiki/Recursive_data_type#Equirecursive_types) such as `list`: <img src="https://render.githubusercontent.com/render/math?math=\text{list}\ \alpha = \mu \tau . 1 %2B \alpha \times \tau">, and `binary tree`: <img src="https://render.githubusercontent.com/render/math?math=\text{tree} = \mu \tau . 1 %2B \text{int} \times \tau \times \tau">. 

The [fix point combinator](https://en.wikipedia.org/wiki/Fixed-point_combinator) `fix` is provided for constructing recursive expressions. 

Additional primitives can be introduced for the purpose of constructing more complex expressions. For example, `pred`, `zero`, and `times` are introduced for constructing a factorial let binding. 

## The Inference System
Below are the inference rules for the type system. 
| Name           |                                                                                            Rule                                                                                             |
| -------------- | :-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| Identifier     |                                            <img src="https://render.githubusercontent.com/render/math?math=\text { A.x: } \tau \vdash x: \tau">                                             |
| Abstraction    |            <img src="https://render.githubusercontent.com/render/math?math=\frac{\text { A.x: } \sigma \vdash e: \tau}{A \vdash(\text { fun }(x) e): \sigma \rightarrow \tau}">             |
| Application    |                <img src="https://render.githubusercontent.com/render/math?math=\frac{A \vdash e: \sigma \rightarrow \tau \quad A \vdash e': \sigma}{A \vdash e(e'): \tau}">                 |
| Let Binding    | <img src="https://render.githubusercontent.com/render/math?math=\frac{A \vdash e': \sigma \quad \text { A.x: } \sigma \vdash e: \tau}{A \vdash (\text { let } x=e' \text { in } e): \tau}"> |
| Generalization |                              <img src="https://render.githubusercontent.com/render/math?math=\frac{A \vdash e: \tau}{A \vdash e: \forall \alpha \cdot \tau}">                               |
| Specialization |                      <img src="https://render.githubusercontent.com/render/math?math=\frac{A \vdash e: \forall \alpha \cdot \tau}{A \vdash e: \tau[\sigma / \alpha]}">                      |


## The Unification Algorithm

[Unification](https://en.wikipedia.org/wiki/Unification_(computer_science)) in the process of inference is to merge two different types or to instantiate a type variable. This is the core of the type inference. This project implements the unification algorithm by treating every type as a node in a forest and employing a [union-find](https://en.wikipedia.org/wiki/Disjoint-set_data_structure) data structure, which is highly efficient.
Pseudo code:
```
boolean unify ( Node m, Node n ) {
    s = find ( m );
    t = find ( n );
    if ( s = t ) 
        return true;
    else if ( nodes s and t represent the same basic type ) 
        return true ;
    else if ( s and t are the same op-node ) {
        union ( s, t );
        return unify ( s.left, t.left ) and unify ( s.right and t.right );
    }
    else if ( s or t represents a variable) {
        union ( s, t );
        return true ;
    }
    else 
        return false ;
}
```

Note that the pseudo code does not consider the direction of the union. However, the direction is important when implementing the union. 

Specifically, we have two cases where the direction is enforced. 

1. If one of the [representative members](https://en.wikipedia.org/wiki/Disjoint-set_data_structure#Representation) for the equivalence classes of `s` and `t` is a non-variable node (e.g. op-node and basic types), union makes that nonvariable node be the representative for the merged equivalence class.
2. In unifying a [non-generic variable](https://en.wikipedia.org/wiki/Parametric_polymorphism) to a term, all the variables contained in that term should become non-generic.

Other than that, union assumes to merge the node provided in the first argument to the node provided in the second argument.

## Acknowledgement

This project is based on the [Python code by Robert Smallshire](https://github.com/rob-smallshire/hindley-milner-python), the [C++ code by Jared Hoberock](https://github.com/jaredhoberock/hindley_milner), and [the paper "Basic Polymorphic Typechecking" by Cardelli](http://lucacardelli.name/Papers/BasicTypechecking.pdf).