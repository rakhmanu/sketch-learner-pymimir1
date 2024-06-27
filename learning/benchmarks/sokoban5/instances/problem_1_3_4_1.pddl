(define (problem p01)
  (:domain ulzhal)
(:objects 
      down - direction 
      left - direction 
      right - direction 
      up - direction 
      robot - thing 
      block01 - thing 
      pos0 - location
      pos1 - location
      pos2 - location
      pos3 - location
)
 (:init
   (at robot pos1)
   (at block01 pos3)
   (clear pos0)
   (clear pos2)

   (is-goal pos2)
   (is-nongoal pos0)
   (is-nongoal pos1)
   (is-nongoal pos3)

   (is-agent robot)
   (is-block block01)
   (move-dir pos0 pos1 right)
   (move-dir pos1 pos0 left)
   (move-dir pos1 pos2 right)
   (move-dir pos2 pos1 left)
   (move-dir pos2 pos3 right)
   (move-dir pos3 pos2 left)
 )
 (:goal (and (at-goal block01) ))
)