(define (problem grid-x3-y2-t2-k20-l20-p100)
(:domain grid)
(:objects 
        f0-0f f1-0f f2-0f 
        f0-1f f1-1f f2-1f 
        shape0 shape1 
        key0-0 key0-1 
)
(:init
(arm-empty)
(place f0-0f)
(place f1-0f)
(place f2-0f)
(place f0-1f)
(place f1-1f)
(place f2-1f)
(shape shape0)
(shape shape1)
(key key0-0)
(key-shape key0-0 shape0)
(key key0-1)
(key-shape key0-1 shape0)
(conn f0-0f f1-0f)
(conn f1-0f f2-0f)
(conn f0-1f f1-1f)
(conn f1-1f f2-1f)
(conn f0-0f f0-1f)
(conn f1-0f f1-1f)
(conn f2-0f f2-1f)
(conn f1-0f f0-0f)
(conn f2-0f f1-0f)
(conn f1-1f f0-1f)
(conn f2-1f f1-1f)
(conn f0-1f f0-0f)
(conn f1-1f f1-0f)
(conn f2-1f f2-0f)
(open f0-0f)
(open f0-1f)
(open f1-1f)
(open f2-1f)
(locked f2-0f)
(lock-shape f2-0f shape0)
(locked f1-0f)
(lock-shape f1-0f shape0)
(at key0-0 f1-1f)
(at key0-1 f2-1f)
(at-robot f1-1f)
)
(:goal
(and
(at key0-0 f1-1f)
(at key0-1 f1-0f)
)
)
)
