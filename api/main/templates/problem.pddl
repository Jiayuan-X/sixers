(define (problem bar)
    (:domain bartending)
    (:objects
		{% for node in locations %}
			{{ node }} - location
		{% endfor %}

		{% for order in orders %}
			{{ order }}	- delivery
		{% endfor %}
    )

    (:init
		{% for a,b in edges.keys %}
			(adj {{ a }} {{ b }})
		{% endfor %}

		(at {{ current_location }} Albert)

		{% for order in orders %}
            (at {{ chef_location }} {{ order }})
			(awaiting {{ order.table_number }} {{ order }})
		{% endfor %}
    )

    (:goal (and
        (forall (?c - delivery) (delivered ?c))
    ))
)