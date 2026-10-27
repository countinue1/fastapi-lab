import redis

r = redis.Redis(host='localhost', port = 6379, decode_responses = True)
print(r.ping())

#存取
r.set('name', '小明')
print(r.get('name'))
#过期
r.set('code', '123456', ex=30)
print(r.ttl('code'))
print(r.get('code'))

#队列：左进右出=先进先出
r.lpush('queue', 'renwu1')
r.lpush('queue', 'renwu2')
print(r.rpop('queue'))

#哈希
r.hset('user', 'name', 'xiaoming')
r.hset('user', 'age', '20')
print(r.hget('user', 'name'))