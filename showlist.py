import whatsup.plan as plan
p = plan.Plan()
list = [n.strip() for n in open('interesting.list', 'rU').readlines()]
p.selectInteresting(list=list)
p.findTransits()
p.printTransits()
