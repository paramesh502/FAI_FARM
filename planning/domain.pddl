(define (domain farm-operations)
  (:requirements :strips :typing :negative-preconditions)
  
  (:types
    plot agent crop - object
    ploughing-agent sowing-agent watering-agent 
    harvesting-agent drone-agent - agent
  )
  
  (:predicates
    (at ?a - agent ?p - plot)
    (plot-state-initial ?p - plot)
    (plot-state-ploughed ?p - plot)
    (plot-state-sown ?p - plot)
    (plot-state-growing ?p - plot)
    (plot-state-healthy ?p - plot)
    (plot-state-ready ?p - plot)
    (plot-needs-water ?p - plot)
    (plot-diseased ?p - plot)
    (agent-idle ?a - agent)
    (agent-busy ?a - agent)
    (crop-planted ?c - crop ?p - plot)
    (adjacent ?p1 - plot ?p2 - plot)
  )
  
  (:action move
    :parameters (?a - agent ?from - plot ?to - plot)
    :precondition (and 
      (at ?a ?from)
      (adjacent ?from ?to)
      (agent-idle ?a)
    )
    :effect (and 
      (not (at ?a ?from))
      (at ?a ?to)
    )
  )
  
  (:action plough
    :parameters (?a - ploughing-agent ?p - plot)
    :precondition (and
      (at ?a ?p)
      (plot-state-initial ?p)
      (agent-idle ?a)
    )
    :effect (and
      (not (plot-state-initial ?p))
      (plot-state-ploughed ?p)
    )
  )
  
  (:action sow
    :parameters (?a - sowing-agent ?p - plot ?c - crop)
    :precondition (and
      (at ?a ?p)
      (plot-state-ploughed ?p)
      (agent-idle ?a)
    )
    :effect (and
      (not (plot-state-ploughed ?p))
      (plot-state-sown ?p)
      (crop-planted ?c ?p)
    )
  )
  
  (:action water
    :parameters (?a - watering-agent ?p - plot)
    :precondition (and
      (at ?a ?p)
      (agent-idle ?a)
      (or 
        (plot-state-sown ?p)
        (plot-needs-water ?p)
        (plot-diseased ?p)
      )
    )
    :effect (and
      (when (plot-state-sown ?p)
        (and 
          (not (plot-state-sown ?p))
          (plot-state-growing ?p)
        )
      )
      (when (plot-needs-water ?p)
        (and
          (not (plot-needs-water ?p))
          (plot-state-growing ?p)
        )
      )
      (when (plot-diseased ?p)
        (not (plot-diseased ?p))
      )
    )
  )
  
  (:action scan
    :parameters (?a - drone-agent ?p - plot)
    :precondition (and
      (at ?a ?p)
      (agent-idle ?a)
      (or 
        (plot-state-growing ?p)
        (plot-state-healthy ?p)
      )
    )
    :effect (and
      ; Scanning may reveal disease (handled by external logic)
    )
  )
  
  (:action harvest
    :parameters (?a - harvesting-agent ?p - plot ?c - crop)
    :precondition (and
      (at ?a ?p)
      (plot-state-ready ?p)
      (crop-planted ?c ?p)
      (agent-idle ?a)
    )
    :effect (and
      (not (plot-state-ready ?p))
      (plot-state-initial ?p)
      (not (crop-planted ?c ?p))
    )
  )
)
