import whatsup.plan as plan
p = plan.Plan()
list = [n.strip() for n in open('interesting.list', 'rU').readlines()]
list = ['WASP94Ab']
p.selectInteresting(list=list)
p.findTransits()
p.printTransits()
