from hashlib import sha1

p = 617665577873
A = 22541923
B = 27623856

E = EllipticCurve(GF(p), [A, B])

G = E([228638339943, 433622854135])
n = 617666383997


# ---------------------------------------#
#                First:                  #
# ---------------------------------------#

P = E([0x2c45f01a2b, 0x137998edd8])
print 'First:\t',hex(G.discrete_log(P))

# ---------------------------------------#
#               Second:                  #
# ---------------------------------------#

m1, m2, m_main = map(lambda x: int(x, 16), raw_input().split(' '))
s1, s2 = 0x17e61e505b, 0x8490a92f23

k = (m1 - m2) * inverse_mod(s1 - s2, n) % n
s_main = 0x41c75eecc
r = 0x5db43ba55e

d = (s_main*k - m_main) * inverse_mod(r, n) % n
print 'Second:\t', hex(d)