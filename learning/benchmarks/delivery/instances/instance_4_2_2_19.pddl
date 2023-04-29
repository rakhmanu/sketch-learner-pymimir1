
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Instance file automatically generated by the Tarski FSTRIPS writer
;;; 
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(define (problem delivery-4x2-2)
    (:domain delivery)

    (:objects
        c_0_0 c_0_1 c_1_0 c_1_1 c_2_0 c_2_1 c_3_0 c_3_1 - cell
        p1 p2 - package
        t1 - truck
    )

    (:init
        (adjacent c_0_1 c_0_0)
        (adjacent c_2_0 c_1_0)
        (adjacent c_3_0 c_2_0)
        (adjacent c_0_0 c_0_1)
        (adjacent c_3_0 c_3_1)
        (adjacent c_3_1 c_2_1)
        (adjacent c_3_1 c_3_0)
        (adjacent c_0_1 c_1_1)
        (adjacent c_0_0 c_1_0)
        (adjacent c_1_1 c_0_1)
        (adjacent c_1_0 c_0_0)
        (adjacent c_1_1 c_2_1)
        (adjacent c_1_0 c_2_0)
        (adjacent c_1_0 c_1_1)
        (adjacent c_1_1 c_1_0)
        (adjacent c_2_1 c_2_0)
        (adjacent c_2_0 c_2_1)
        (adjacent c_2_1 c_3_1)
        (adjacent c_2_0 c_3_0)
        (adjacent c_2_1 c_1_1)
        (at p2 c_1_1)
        (at t1 c_0_1)
        (at p1 c_1_1)
        (empty t1)
    )

    (:goal
        (and (at p1 c_0_1) (at p2 c_0_1))
    )

    
    
    
)

