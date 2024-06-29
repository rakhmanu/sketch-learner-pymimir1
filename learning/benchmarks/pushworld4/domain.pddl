(define
    (domain m14)
    (:requirements :typing :strips :conditional-effects :negative-preconditions)

    (:types
        position - object
        direction - object

        ; Any object that can move and push other objects
        moveable-object - object

        ; The object that can be directly controlled
        agent-object - moveable-object

        ; A pair of objects, only used for BFWS. This is an auxiliary type to reduce
        ; the arity of the `in-collision` predicate. BFWS uses the `libff` library from
        ; LAPKT, and `libff` allocates memory for (num constants)^(predicate arity),
        ; which can exceed 100 Gb in some problems when `in-collision` has arity=4.
        object-pair - object
    )

    (:constants
        agent - agent-object
        up down left right - direction
        m1 m2 m3 m4 m5 m6 m7 m8 m9 m10 m11 m12 m13 m14 - moveable-object
        
    )

    (:predicates
        (should-move ?obj - moveable-object ?dir - direction)
        (has-moved ?obj - moveable-object)
        (at ?obj - moveable-object ?pos - position)
        (connected ?from - position ?to - position ?dir - direction)
        (wall-collision ?obj - moveable-object ?next-pos - position)
        
        (in-collision
            ?obj - moveable-object
            ?pos - position
            ?other-obj - moveable-object
            ?other-pos - position
        )

        
    )

    (:action move-agent
        :parameters (?dir - direction)
        :precondition (and
            (not (should-move agent left))
            (not (should-move agent right))
            (not (should-move agent up))
            (not (should-move agent down))
            (not (should-move m1 left))
            (not (should-move m1 right))
            (not (should-move m1 up))
            (not (should-move m1 down))
            (not (should-move m2 left))
            (not (should-move m2 right))
            (not (should-move m2 up))
            (not (should-move m2 down))
            (not (should-move m3 left))
            (not (should-move m3 right))
            (not (should-move m3 up))
            (not (should-move m3 down))
            (not (should-move m4 left))
            (not (should-move m4 right))
            (not (should-move m4 up))
            (not (should-move m4 down))
            (not (should-move m5 left))
            (not (should-move m5 right))
            (not (should-move m5 up))
            (not (should-move m5 down))
            (not (should-move m6 left))
            (not (should-move m6 right))
            (not (should-move m6 up))
            (not (should-move m6 down))
            (not (should-move m7 left))
            (not (should-move m7 right))
            (not (should-move m7 up))
            (not (should-move m7 down))
            (not (should-move m8 left))
            (not (should-move m8 right))
            (not (should-move m8 up))
            (not (should-move m8 down))
            (not (should-move m9 left))
            (not (should-move m9 right))
            (not (should-move m9 up))
            (not (should-move m9 down))
            (not (should-move m10 left))
            (not (should-move m10 right))
            (not (should-move m10 up))
            (not (should-move m10 down))
            (not (should-move m11 left))
            (not (should-move m11 right))
            (not (should-move m11 up))
            (not (should-move m11 down))
            (not (should-move m12 left))
            (not (should-move m12 right))
            (not (should-move m12 up))
            (not (should-move m12 down))
            (not (should-move m13 left))
            (not (should-move m13 right))
            (not (should-move m13 up))
            (not (should-move m13 down))
            (not (should-move m14 left))
            (not (should-move m14 right))
            (not (should-move m14 up))
            (not (should-move m14 down))
        )
        :effect (and
            (should-move agent ?dir)
            (forall
                (?obj - moveable-object)
                (not (has-moved ?obj)))
        )
    )

    (:action push
        :parameters ( ?obj - moveable-object ?dir - direction ?pos - position ?next-pos - position
        )
        :precondition (and
            (should-move ?obj ?dir)
            (not (has-moved ?obj))
            (at ?obj ?pos)
            (connected ?pos ?next-pos ?dir)
            (not (wall-collision ?obj ?next-pos))
        )
        :effect (and
            (not (at ?obj ?pos))
            (at ?obj ?next-pos)
            (has-moved ?obj)
            (not (should-move ?obj ?dir))
            (forall (?other-obj - moveable-object)
                (when
                    (and
                        (not (has-moved ?other-obj))
                        (exists (?other-pos - position)
                            (and
                                (at ?other-obj ?other-pos)
                                (in-collision ?obj ?next-pos ?other-obj ?other-pos)
                            )
                        )

                    )
                    (should-move ?other-obj ?dir)
                )
            )
        )
    )
)