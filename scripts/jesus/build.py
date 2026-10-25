"""Write data/jesus.json: the places the Gospels record Our Lord going, and the moments of His life in order.

References follow the NABRE (bible.usccb.org). The order follows a traditional harmony of the four Gospels, checked against the Mysteries of the Rosary
(Joyful: Annunciation, Visitation, Nativity, Presentation, Finding; Luminous; Sorrowful; Glorious).
cert: sure = the place itself is known; trad = the town or area is known and the exact spot is honoured by long tradition;
debated = more than one site is proposed. An event's u note flags a placement less certain than its place.

usage: python3 scripts/jesus/build.py
"""
import json, os

# id, name, modern location, [lat, lon], cert, location note, English Wikipedia title for the photo, Bible Places id, zoom
P = [
 ('nazareth', 'Nazareth', 'Basilica of the Annunciation, Nazareth', [32.7022, 35.2973], 'sure', "The town of the Holy Family in Lower Galilee. The Basilica of the Annunciation stands over the grotto venerated as the home of the Virgin Mary, and the Church of Saint Joseph nearby recalls the carpenter's workshop.", 'Basilica of the Annunciation', 'nazareth', 15),
 ('einkarem', 'Ein Karem', 'Church of the Visitation, Ein Karem', [31.7647, 35.1569], 'trad', "Saint Luke names only \"a town of Judah\" in the hill country (Luke 1:39). Since the early centuries tradition has honoured Ein Karem, west of Jerusalem, as the home of Zechariah and Elizabeth.", 'Church of the Visitation', 'einkarem', 14),
 ('bethlehem', 'Bethlehem', 'Church of the Nativity, Bethlehem', [31.7043, 35.2073], 'sure', "The town of David. Saint Justin Martyr already wrote in the second century of the cave where Christ was born; the Grotto of the Nativity lies beneath the basilica built by Saint Helena.", 'Church of the Nativity', 'bethlehem', 15),
 ('shepherds', "Shepherds' Field", 'Beit Sahour, east of Bethlehem', [31.7066, 35.2256], 'trad', "Luke says the shepherds were \"in that region\" (Luke 2:8). The Franciscan Shepherds' Field chapel in Beit Sahour keeps the memory of the angels' song.", 'Beit Sahour', None, 14),
 ('temple', 'The Temple in Jerusalem', 'Temple Mount, Old City of Jerusalem', [31.7780, 35.2354], 'sure', "The platform of Herod's Temple, the house of the Father where Our Lord was presented, was found at twelve, and taught at the great feasts.", 'Temple Mount', 'jerusalem', 15.5),
 ('egypt', 'Egypt', 'Church of Saints Sergius and Bacchus, Old Cairo', [30.0057, 31.2302], 'debated', "Saint Matthew names only Egypt. Coptic tradition traces the Holy Family's route through many towns along the Nile; the crypt of Saints Sergius and Bacchus in Old Cairo is honoured as one of their resting places.", 'Saints Sergius and Bacchus Church (Cairo)', 'cairo', 13),
 ('jordan', 'Bethany across the Jordan', 'Al-Maghtas and Qasr al-Yahud, near Jericho', [31.8375, 35.5450], 'trad', "Saint John places the baptism at \"Bethany across the Jordan\" (John 1:28). The traditional site lies on both banks of the river east of Jericho: Al-Maghtas in Jordan and Qasr al-Yahud on the west bank.", 'Al-Maghtas', 'jordan', 13),
 ('desert', 'The Judean desert', 'Mount of Temptation, above Jericho', [31.8714, 35.4294], 'trad', "The Gospels say only \"the desert\". Tradition honours the Mount of Temptation above Jericho, where a Greek Orthodox monastery clings to the cliff.", 'Mount of Temptation', None, 13),
 ('cana', 'Cana in Galilee', 'Kafr Kanna, near Nazareth', [32.7466, 35.3397], 'debated', "Pilgrims have long honoured Kafr Kanna, where the Franciscan Wedding Church stands. Some scholars prefer Khirbet Qana, a ruin about 13 km to the north.", 'Kafr Kanna', 'cana', 14),
 ('capernaum', 'Capernaum', 'Capernaum, on the Sea of Galilee', [32.8806, 35.5750], 'sure', "\"His own town\" (Matthew 9:1), the center of His Galilean ministry. Pilgrims see the white synagogue built over an earlier one, and the house of Saint Peter beneath a modern church.", 'Capernaum', 'capernaum', 15),
 ('sea', 'The Sea of Galilee', 'Sea of Galilee (Lake of Gennesaret, Sea of Tiberias)', [32.8300, 35.5900], 'sure', "The lake at the heart of Our Lord's ministry, where the apostles fished and where He calmed the wind and waves.", 'Sea of Galilee', None, 11),
 ('jacobswell', "Jacob's Well", 'Bir Ya\'qub, Nablus (ancient Sychar)', [32.2097, 35.2853], 'sure', "One of the most securely identified places in the Gospels: the well Jacob dug, now inside a Greek Orthodox church at the foot of Mount Gerizim.", "Jacob's Well", 'shechem', 15),
 ('beatitudes', 'Mount of Beatitudes', 'Church of the Beatitudes, above Tabgha', [32.8814, 35.5567], 'trad', "Matthew says only that He \"went up the mountain\" (Matthew 5:1). The hill above Tabgha has been honoured since the fourth century; today's church has eight sides, for the eight Beatitudes.", 'Mount of Beatitudes', 'beatitudes', 15),
 ('nain', 'Nain', 'Nein, south of Mount Tabor', [32.6306, 35.3478], 'sure', "A small village on the slope of the Hill of Moreh. A Franciscan chapel marks where Our Lord met the funeral procession.", 'Nein', 'nain', 15),
 ('bethesda', 'Pool of Bethesda', 'Church of Saint Anne, Old City of Jerusalem', [31.7815, 35.2359], 'sure', "Archaeologists have uncovered the pool with five porticoes beside the Church of Saint Anne, honoured as the birthplace of the Virgin Mary.", 'Pool of Bethesda', None, 16),
 ('kursi', 'Territory of the Gerasenes', 'Kursi, on the eastern shore of the Sea of Galilee', [32.8259, 35.6503], 'debated', "Mark and Luke say \"the territory of the Gerasenes\", Matthew \"of the Gadarenes\". A Byzantine monastery at Kursi, on the eastern shore, marks the traditional place.", 'Kursi, Sea of Galilee', 'kursi', 14),
 ('tabgha', 'Tabgha', 'Church of the Multiplication, Tabgha', [32.8732, 35.5493], 'trad', "Luke sets the feeding near Bethsaida (Luke 9:10). Since the fourth century pilgrims have honoured it at Tabgha, where the famous mosaic of the loaves and fishes lies before the altar.", 'Church of the Multiplication', 'tabgha', 16),
 ('tyre', 'District of Tyre and Sidon', 'Tyre, Lebanon', [33.2705, 35.1965], 'sure', "The Phoenician coast north of Galilee, the one journey of Our Lord outside the land of Israel during His ministry.", 'Tyre, Lebanon', 'tyre', 12),
 ('decapolis', 'The Decapolis', 'Hippos (Sussita), above the eastern shore', [32.7790, 35.6580], 'debated', "Mark says He went \"into the district of the Decapolis\" (Mark 7:31), a league of Greek cities east of the lake. The exact place of these signs is not named; Hippos, the Decapolis city nearest the lake, stands for the region here.", 'Hippos', None, 12),
 ('magdala', 'Magadan', 'Magdala, on the western shore', [32.8250, 35.5150], 'debated', "Matthew writes Magadan, Mark Dalmanutha (Mark 8:10). Many identify the place with Magdala, the home town of Saint Mary Magdalene, where a first-century synagogue has been found.", 'Magdala', 'magdala', 15),
 ('bethsaida', 'Bethsaida', 'Bethsaida, north of the Sea of Galilee', [32.9103, 35.6306], 'debated', "The home of Peter, Andrew and Philip (John 1:44). Archaeologists dispute between et-Tell and el-Araj, near the Jordan's entry into the lake.", 'Bethsaida', None, 14),
 ('caesarea', 'Caesarea Philippi', 'Banias, at the foot of Mount Hermon', [33.2486, 35.6943], 'sure', "A pagan city at the springs of the Jordan, under a great rock face. Here, before shrines to the god Pan, Peter confessed Jesus as the Christ.", 'Banias', 'caesareaphilippi', 15),
 ('tabor', 'Mount Tabor', 'Basilica of the Transfiguration, Mount Tabor', [32.6869, 35.3900], 'trad', "The Gospels say \"a high mountain\" (Mark 9:2). Since Origen and Saint Cyril of Jerusalem, tradition has named Tabor; the Franciscan basilica crowns its summit.", 'Mount Tabor', 'tabor', 14),
 ('chorazin', 'Chorazin', 'Korazim, above Capernaum', [32.9113, 35.5640], 'sure', "A town of black basalt in the hills above Capernaum, one of the places where \"most of His mighty deeds had been done\" (Matthew 11:20-21).", 'Chorazin', None, 15),
 ('bethany', 'Bethany', 'Al-Eizariya, on the Mount of Olives', [31.7714, 35.2614], 'sure', "The village of Martha, Mary and Lazarus on the far slope of the Mount of Olives. The tomb of Lazarus and a Franciscan church are visited there.", 'Church of Saint Lazarus, Bethany', 'bethany', 15.5),
 ('siloam', 'Pool of Siloam', 'City of David, Jerusalem', [31.7705, 35.2354], 'sure', "The pool at the south end of the City of David, fed by Hezekiah's tunnel. Its first-century steps were uncovered in 2004.", 'Pool of Siloam', None, 16),
 ('eleona', 'Mount of Olives', 'Church of the Pater Noster (Eleona), Mount of Olives', [31.7785, 35.2433], 'trad', "Saint Helena built the Eleona church over a cave where tradition says Our Lord taught His disciples. The Our Father is written on its walls in more than 140 languages.", 'Church of the Pater Noster', 'olives', 16),
 ('ephraim', 'Ephraim', 'Taybeh, north-east of Jerusalem', [31.9550, 35.3000], 'debated', "John says only that it was a town near the desert (John 11:54). Tradition places it at Taybeh, today a Christian village.", 'Taybeh', None, 14),
 ('jericho', 'Jericho', 'Jericho', [31.8560, 35.4600], 'sure', "The oasis city on the road up to Jerusalem. A sycamore tree in the town recalls Zacchaeus.", 'Jericho', 'jericho', 14),
 ('bethphage', 'Bethphage', 'Franciscan church of Bethphage, Mount of Olives', [31.7790, 35.2560], 'trad', "The village where the disciples found the colt. The Palm Sunday procession of the Church in Jerusalem still begins here each year.", 'Bethphage', None, 16),
 ('flevit', 'Dominus Flevit', 'Church of Dominus Flevit, Mount of Olives', [31.7778, 35.2420], 'trad', "A small church shaped like a teardrop, looking across the Kidron to the city, recalls where \"the Lord wept\".", 'Dominus Flevit Church', None, 16.5),
 ('cenacle', 'The Upper Room', 'The Cenacle, Mount Zion', [31.7717, 35.2290], 'trad', "The early Church honoured Mount Zion as the place of the Last Supper and of Pentecost. The present Gothic room dates from the Crusades and the Franciscans.", 'Cenacle', 'jerusalem', 16.5),
 ('gethsemane', 'Gethsemane', 'Church of All Nations, at the foot of the Mount of Olives', [31.7793, 35.2396], 'trad', "The garden of ancient olive trees, with the Church of All Nations built over the rock where Our Lord prayed in agony.", 'Church of All Nations', 'olives', 16.5),
 ('caiaphas', 'House of Caiaphas', 'Saint Peter in Gallicantu, Mount Zion', [31.7716, 35.2317], 'trad', "The Church of Saint Peter in Gallicantu (\"at the cock's crow\") keeps the memory of Peter's denial and of the night Our Lord spent in prison. Others place the high priest's house nearer the Cenacle.", 'Church of Saint Peter in Gallicantu', None, 16.5),
 ('praetorium', 'The Praetorium', 'Church of the Flagellation and Ecce Homo arch, Via Dolorosa', [31.7808, 35.2337], 'debated', "The Way of the Cross begins at the Antonia fortress, where the Franciscans keep the Chapels of the Flagellation and Condemnation. Many scholars place Pilate instead at Herod's palace near the Jaffa Gate.", 'Church of the Flagellation', None, 16.5),
 ('viadolorosa', 'Via Dolorosa', 'The Way of the Cross, Old City of Jerusalem', [31.7797, 35.2318], 'trad', "Since the Middle Ages pilgrims have prayed the Stations of the Cross along this street from the Antonia fortress to Calvary; the Franciscans lead the procession every Friday. The exact route Our Lord walked depends on where Pilate judged Him.", 'Via Dolorosa', None, 16.5),
 ('calvary', 'Calvary and the Holy Sepulchre', 'Church of the Holy Sepulchre, Jerusalem', [31.7784, 35.2296], 'trad', "Christians have honoured this place since the first generations; Saint Helena and Constantine built the basilica over the rock of Golgotha and the empty tomb, and the Franciscans serve there today.", 'Church of the Holy Sepulchre', 'sepulchre', 16.5),
 ('emmaus', 'Emmaus', 'Emmaus Nicopolis, near Latrun', [31.8395, 34.9897], 'debated', "Luke gives the distance as about seven miles from Jerusalem (Luke 24:13). Three sites are honoured: Emmaus Nicopolis, shown here; El-Qubeibeh, kept by the Franciscans; and Abu Ghosh.", 'Emmaus Nicopolis', 'emmaus', 14),
 ('primacy', 'Shore of the Sea of Tiberias', 'Church of the Primacy of Saint Peter, Tabgha', [32.8718, 35.5480], 'trad', "A small basalt church on the water's edge is built around the rock called Mensa Christi, the table of Christ, where tradition says He served breakfast to the apostles.", 'Church of the Primacy of Saint Peter', None, 16.5),
 ('ascension', 'Place of the Ascension', 'Chapel of the Ascension, Mount of Olives', [31.7787, 35.2447], 'trad', "Luke says He led them \"as far as Bethany\" (Luke 24:50), and Acts that they returned from the Mount of Olives (Acts 1:12). A small chapel at the summit keeps a rock honoured as bearing His last footprint.", 'Chapel of the Ascension, Jerusalem', 'olives', 16.5),
]

# era, place, title, references, text, optional note when the event's place is less certain than the place itself
E = [
 ('hidden', 'nazareth', 'The Annunciation', 'Luke 1:26-38', "The angel Gabriel greets the Virgin Mary, full of grace. At her \"May it be done to me according to your word\", the Word becomes flesh in her womb."),
 ('hidden', 'einkarem', 'The Visitation', 'Luke 1:39-56', "Mary carries Our Lord to her kinswoman Elizabeth. John leaps for joy in the womb, Elizabeth calls her \"the mother of my Lord\", and Mary sings the Magnificat."),
 ('hidden', 'bethlehem', 'The Birth of Our Lord', 'Luke 2:1-7; Matthew 1:18-25', "Our Lord is born of the Virgin Mary in the city of David, wrapped in swaddling clothes and laid in a manger, because there was no room for them in the inn."),
 ('hidden', 'shepherds', 'The shepherds hear the angels', 'Luke 2:8-20', "An angel announces \"a savior who is Messiah and Lord\", and the heavenly host sings \"Glory to God in the highest\". The shepherds hurry to find the Child."),
 ('hidden', 'bethlehem', 'The Magi adore the Child', 'Matthew 2:1-12', "Wise men from the East follow His star, find the Child with Mary His mother, and offer gold, frankincense and myrrh."),
 ('hidden', 'temple', 'The Presentation in the Temple', 'Luke 2:22-38', "Mary and Joseph present the Child to the Lord. Simeon takes Him in his arms, calls Him \"a light for revelation to the Gentiles\", and tells Mary a sword will pierce her heart."),
 ('hidden', 'egypt', 'The Flight into Egypt', 'Matthew 2:13-15', "Warned in a dream, Saint Joseph rises by night and takes the Child and His mother into Egypt, beyond the reach of Herod, fulfilling \"Out of Egypt I called my son\" (Hosea 11:1)."),
 ('hidden', 'nazareth', 'The return to Nazareth', 'Matthew 2:19-23; Luke 2:39-40', "After Herod's death the Holy Family settles in Nazareth, and \"the child grew and became strong, filled with wisdom; and the favor of God was upon him\"."),
 ('hidden', 'temple', 'The Finding in the Temple', 'Luke 2:41-50', "At twelve He stays behind in Jerusalem after Passover. On the third day Mary and Joseph find Him among the teachers: \"Did you not know that I must be in my Father's house?\""),
 ('hidden', 'nazareth', 'The hidden life', 'Luke 2:51-52; Mark 6:3', "For some thirty years He lives at Nazareth, obedient to Mary and Joseph, working as a carpenter and advancing in wisdom and age and favor before God and man."),

 ('ministry', 'jordan', 'The Baptism of the Lord', 'Matthew 3:13-17; Mark 1:9-11; Luke 3:21-22', "John baptizes Him in the Jordan. The heavens open, the Holy Spirit descends like a dove, and the Father's voice says: \"This is my beloved Son, with whom I am well pleased.\""),
 ('ministry', 'desert', 'Forty days in the desert', 'Matthew 4:1-11; Luke 4:1-13', "Led by the Spirit into the desert, He fasts forty days and forty nights and overcomes the temptations of the devil with the word of God."),
 ('ministry', 'jordan', 'The first disciples', 'John 1:35-51', "John points Him out: \"Behold, the Lamb of God.\" Andrew brings his brother Simon, whom Jesus names Cephas, Peter; Philip and Nathanael follow."),
 ('ministry', 'cana', 'The wedding at Cana', 'John 2:1-11', "At His mother's word, \"Do whatever he tells you\", He changes water into wine, the first of His signs, and His disciples begin to believe in Him."),
 ('ministry', 'temple', 'The first Passover: zeal for His Father\'s house', 'John 2:13-25; John 3:1-21', "He drives the money changers from the Temple, and by night teaches Nicodemus that one must be born of water and Spirit. \"God so loved the world that he gave his only Son.\""),
 ('ministry', 'jacobswell', 'The woman at the well', 'John 4:4-42', "Weary at noon, He asks a Samaritan woman for a drink and offers her living water, \"a spring of water welling up to eternal life\". Many in her town come to believe."),
 ('ministry', 'cana', "Healing the official's son", 'John 4:46-54', "A royal official from Capernaum begs Him to come. \"You may go; your son will live.\" The boy is healed at that very hour."),
 ('ministry', 'nazareth', 'Rejected at Nazareth', 'Luke 4:16-30', "In the synagogue He reads Isaiah, \"The Spirit of the Lord is upon me\", and says, \"Today this scripture passage is fulfilled.\" His own townspeople drive Him toward the brow of the hill, but He passes through their midst.", "The Franciscans honour the Mount of the Precipice south of the town as the hill of Luke 4:29."),
 ('ministry', 'capernaum', 'The Kingdom of God is at hand', 'Matthew 4:12-17; Mark 1:14-15', "Leaving Nazareth, He makes His home in Capernaum by the sea and begins to preach: \"This is the time of fulfillment. The kingdom of God is at hand. Repent, and believe in the gospel.\""),
 ('ministry', 'capernaum', 'Fishers of men', 'Mark 1:16-20; Luke 5:1-11', "By the shore He calls Simon and Andrew, James and John: \"Come after me, and I will make you fishers of men.\" After the miraculous catch they leave everything and follow Him."),
 ('ministry', 'capernaum', 'Healing in Capernaum', 'Mark 1:21-34', "He teaches with authority in the synagogue, frees a man from an unclean spirit, raises Peter's mother-in-law from her fever, and at sunset the whole town gathers at the door."),
 ('ministry', 'capernaum', 'The paralytic and the call of Matthew', 'Mark 2:1-17', "Friends lower a paralyzed man through the roof; Jesus forgives his sins and bids him walk. Then He calls Levi, Matthew, from his customs post: \"Follow me.\""),
 ('ministry', 'beatitudes', 'The Sermon on the Mount', 'Matthew 5-7', "He teaches the Beatitudes, \"Blessed are the poor in spirit, for theirs is the kingdom of heaven\", the new law of love, and the Our Father."),
 ('ministry', 'capernaum', "The centurion's servant", 'Matthew 8:5-13; Luke 7:1-10', "A Roman centurion says, \"Lord, I am not worthy to have you enter under my roof; only say the word.\" The Church echoes his words before Holy Communion at every Mass."),
 ('ministry', 'nain', "The widow's son", 'Luke 7:11-17', "Moved with pity for a widow burying her only son, He touches the bier: \"Young man, I tell you, arise!\" and gives him back to his mother."),
 ('ministry', 'bethesda', 'The man at the pool', 'John 5:1-18', "At a feast in Jerusalem He heals a man ill for thirty-eight years: \"Rise, take up your mat, and walk.\""),
 ('ministry', 'sea', 'Calming the storm', 'Mark 4:35-41', "A violent squall swamps the boat while He sleeps. He rebukes the wind, \"Quiet! Be still!\", and there is great calm. \"Who then is this whom even wind and sea obey?\""),
 ('ministry', 'kursi', 'The man possessed by Legion', 'Mark 5:1-20', "On the far shore He frees a man tormented by many demons, who are sent into a herd of swine. The man asks to follow Him and is sent to proclaim what the Lord has done."),
 ('ministry', 'capernaum', "Jairus' daughter", 'Mark 5:21-43', "A woman is healed by touching His cloak, and He takes the dead daughter of Jairus by the hand: \"Talitha koum\", \"Little girl, I say to you, arise!\""),
 ('ministry', 'tabgha', 'Feeding the five thousand', 'Mark 6:30-44; John 6:1-15', "With five loaves and two fish He feeds the multitude, looking up to heaven, blessing and breaking the bread, and twelve baskets of fragments are left over."),
 ('ministry', 'sea', 'Walking on the water', 'Matthew 14:22-33', "In the fourth watch of the night He comes to the disciples walking on the sea. Peter walks toward Him, begins to sink, and cries, \"Lord, save me!\""),
 ('ministry', 'capernaum', 'The Bread of Life', 'John 6:22-69', "In the synagogue at Capernaum He teaches, \"I am the bread of life ... whoever eats my flesh and drinks my blood has eternal life.\" Peter answers, \"Master, to whom shall we go?\""),
 ('ministry', 'tyre', "The Canaanite woman's faith", 'Matthew 15:21-28; Mark 7:24-30', "A Gentile mother begs Him to heal her daughter: \"Even the dogs eat the scraps that fall from the table of their masters.\" \"O woman, great is your faith!\""),
 ('ministry', 'decapolis', 'Ephphatha, and four thousand fed', 'Mark 7:31-37; Mark 8:1-10', "He opens the ears of a deaf man, \"Ephphatha, be opened\", and with seven loaves feeds four thousand who had stayed with Him three days."),
 ('ministry', 'magdala', 'The sign of Jonah', 'Matthew 15:39; Matthew 16:1-4', "Pharisees and Sadducees ask for a sign from heaven. He tells them no sign will be given but the sign of Jonah."),
 ('ministry', 'bethsaida', 'The blind man of Bethsaida', 'Mark 8:22-26', "He leads a blind man out of the village by the hand and lays His hands on him twice, until he sees everything distinctly."),
 ('ministry', 'caesarea', '"You are the Christ"', 'Matthew 16:13-20', "\"Who do you say that I am?\" Peter answers, \"You are the Messiah, the Son of the living God.\" \"You are Peter, and upon this rock I will build my church ... I will give you the keys to the kingdom of heaven.\""),
 ('ministry', 'tabor', 'The Transfiguration', 'Matthew 17:1-8; Mark 9:2-8; Luke 9:28-36', "Before Peter, James and John His face shines like the sun, Moses and Elijah speak with Him, and the Father says, \"This is my beloved Son ... listen to him.\""),
 ('ministry', 'chorazin', 'Woe to you, Chorazin', 'Matthew 11:20-24', "He reproaches the towns where most of His mighty deeds had been done, Chorazin, Bethsaida and Capernaum, for they did not repent."),
 ('ministry', 'capernaum', 'Like little children', 'Matthew 17:24-27; Matthew 18:1-5', "Peter finds the Temple tax in the mouth of a fish. Then Jesus sets a child in their midst: \"Unless you turn and become like children, you will not enter the kingdom of heaven.\""),

 ('journey', 'temple', 'The Feast of Tabernacles', 'John 7:14-39; John 8:1-12', "He teaches in the Temple courts, \"Let anyone who thirsts come to me and drink\", forgives the woman caught in adultery, \"Go, and from now on do not sin any more\", and proclaims, \"I am the light of the world.\""),
 ('journey', 'siloam', 'The man born blind', 'John 9:1-41', "He smears clay on the eyes of a man blind from birth and sends him to wash in the Pool of Siloam. He comes back able to see, and worships Him: \"I do believe, Lord.\""),
 ('journey', 'bethany', 'Martha and Mary', 'Luke 10:38-42', "Martha welcomes Him while Mary sits at His feet listening. \"Mary has chosen the better part and it will not be taken from her.\"", "Luke says only \"a village\"; John names Bethany as the home of Martha and Mary (John 11:1)."),
 ('journey', 'eleona', 'Lord, teach us to pray', 'Luke 11:1-4', "When a disciple asks Him to teach them to pray, He gives them the Our Father.", "Luke does not name the place; tradition remembers it at the Eleona cave on the Mount of Olives. Matthew gives the prayer in the Sermon on the Mount (Matthew 6:9-13)."),
 ('journey', 'temple', 'The Feast of the Dedication', 'John 10:22-39', "Walking in the portico of Solomon in winter, He says, \"My sheep hear my voice ... The Father and I are one.\""),
 ('journey', 'jordan', 'Across the Jordan', 'John 10:40-42; Mark 10:1-16', "He returns to where John first baptized. He teaches that what God has joined together no one must separate, and blesses the children: \"Let the children come to me.\""),
 ('journey', 'bethany', 'The raising of Lazarus', 'John 11:1-44', "\"I am the resurrection and the life.\" Jesus weeps at the tomb of His friend, then cries out, \"Lazarus, come out!\", and the dead man walks out, still bound."),
 ('journey', 'ephraim', 'Withdrawal to Ephraim', 'John 11:54', "As the council plots His death, He withdraws with His disciples to a town near the desert called Ephraim."),
 ('journey', 'jericho', 'Bartimaeus and Zacchaeus', 'Mark 10:46-52; Luke 19:1-10', "Blind Bartimaeus cries, \"Jesus, son of David, have pity on me!\" and receives his sight. Zacchaeus climbs a sycamore to see Him: \"Today salvation has come to this house.\""),
 ('journey', 'bethany', 'Anointed at Bethany', 'John 12:1-8; Mark 14:3-9', "Six days before Passover, Mary anoints His feet with costly nard, and the house is filled with its fragrance. He receives it as an anointing for His burial."),

 ('passion', 'bethphage', 'Palm Sunday', 'Matthew 21:1-11; Luke 19:29-40', "He rides into Jerusalem on a colt as the crowds spread their cloaks and branches: \"Hosanna to the Son of David; blessed is he who comes in the name of the Lord.\""),
 ('passion', 'flevit', 'He weeps over Jerusalem', 'Luke 19:41-44', "As He comes in sight of the city He weeps over it: \"If this day you only knew what makes for peace.\""),
 ('passion', 'temple', 'Teaching in the Temple', 'Mark 11:15-19; Mark 12:41-44', "He overturns the tables, \"My house shall be called a house of prayer for all peoples\", and praises the poor widow who gives her last two coins."),
 ('passion', 'eleona', 'The end of the age', 'Mark 13:1-37; Matthew 25:31-46', "Seated on the Mount of Olives facing the Temple, He tells of its destruction and of His coming in glory: \"Whatever you did for one of these least brothers of mine, you did for me.\""),
 ('passion', 'cenacle', 'The Last Supper', 'Luke 22:7-38; John 13:1-17; 1 Corinthians 11:23-26', "He washes His disciples' feet, and taking bread and wine says, \"This is my body ... This cup is the new covenant in my blood ... Do this in memory of me\", giving the Church the Holy Eucharist and the priesthood."),
 ('passion', 'gethsemane', 'The Agony in the Garden', 'Matthew 26:36-56; Luke 22:39-53', "He prays in anguish, His sweat like drops of blood: \"Father, not my will but yours be done.\" Judas comes with a crowd and betrays Him with a kiss."),
 ('passion', 'caiaphas', "Before Caiaphas; Peter's denial", 'Matthew 26:57-75; John 18:12-27', "Bound, He is led before Annas and the high priest Caiaphas and condemned for blasphemy. In the courtyard Peter denies Him three times, the cock crows, and Peter weeps bitterly."),
 ('passion', 'praetorium', 'Before Pilate', 'Luke 23:1-25; John 18:28-40', "Pilate finds no guilt in Him and sends Him to Herod, who mocks Him and sends Him back. The crowd cries out for Barabbas, and Pilate gives in to their demand."),
 ('passion', 'praetorium', 'The Scourging at the Pillar', 'John 19:1; Mark 15:15', "\"Then Pilate took Jesus and had him scourged.\" \"By his wounds we were healed\" (Isaiah 53:5)."),
 ('passion', 'praetorium', 'The Crowning with Thorns', 'Mark 15:16-20; John 19:2-16', "The soldiers weave a crown of thorns, clothe Him in purple and mock Him: \"Hail, King of the Jews!\" Pilate brings Him out: \"Behold, the man!\" and hands Him over to be crucified."),
 ('passion', 'viadolorosa', 'The Carrying of the Cross', 'John 19:17; Luke 23:26-32', "Carrying the cross Himself, He goes out toward Golgotha. Simon of Cyrene is made to help Him, and He tells the weeping women, \"Daughters of Jerusalem, do not weep for me; weep instead for yourselves and for your children.\""),
 ('passion', 'calvary', 'The Crucifixion', 'Luke 23:33-49; John 19:18-37', "He is crucified between two thieves. \"Father, forgive them, they know not what they do.\" \"Today you will be with me in Paradise.\" \"Woman, behold, your son ... Behold, your mother.\" \"It is finished.\" He bows His head and hands over the spirit."),
 ('passion', 'calvary', 'Laid in the tomb', 'Matthew 27:57-61; John 19:38-42', "Joseph of Arimathea and Nicodemus wrap His body in linen with spices and lay Him in a new tomb hewn in the rock, in a garden near the place of the cross."),

 ('risen', 'calvary', 'The Resurrection', 'Matthew 28:1-10; John 20:1-18', "On the first day of the week the tomb is empty. The risen Lord calls Mary Magdalene by name and sends her to the apostles: \"I have seen the Lord.\""),
 ('risen', 'emmaus', 'The road to Emmaus', 'Luke 24:13-35', "He walks unrecognized with two disciples, opening the Scriptures to them, and is known to them in the breaking of the bread. \"Were not our hearts burning within us?\""),
 ('risen', 'cenacle', 'Peace be with you', 'Luke 24:36-49; John 20:19-29', "He stands among the apostles behind locked doors, breathes on them, \"Receive the holy Spirit. Whose sins you forgive are forgiven them\", and a week later Thomas confesses, \"My Lord and my God!\""),
 ('risen', 'primacy', '"Feed my sheep"', 'John 21:1-19', "At dawn by the lake He fills the apostles' nets and cooks them breakfast. Three times He asks Peter, \"Do you love me?\" and three times entrusts him: \"Feed my sheep.\""),
 ('risen', 'beatitudes', 'The Great Commission', 'Matthew 28:16-20', "On the mountain in Galilee He sends the Eleven: \"Go, therefore, and make disciples of all nations, baptizing them in the name of the Father, and of the Son, and of the holy Spirit ... I am with you always.\"", "Matthew does not name the mountain. Pilgrims often recall it on the Mount of Beatitudes; others think of Tabor or Mount Arbel."),
 ('risen', 'ascension', 'The Ascension', 'Luke 24:50-53; Acts 1:6-12', "Forty days after Easter He blesses the apostles, promises them the Holy Spirit, and is taken up to heaven before their eyes, while they return to Jerusalem with great joy."),
]

ERAS = [('hidden', '#9ec5ff'), ('ministry', '#7ccf9a'), ('journey', '#f3d58c'), ('passion', '#e0625a'), ('risen', '#fdf6e3')]

SMALL = set('a an and as at by for from in into of on or the to with'.split())
def title(t):
    """Title Case for event names: small words stay lowercase except first and after a colon."""
    out, cap = [], True
    for w in t.split(' '):
        lead = len(w) - len(w.lstrip('"'))
        core = w[lead:]
        if core and (cap or core.lower() not in SMALL):
            core = core[0].upper() + core[1:]
        elif core.lower() in SMALL:
            core = core.lower()
        out.append(w[:lead] + core)
        cap = w.endswith(':') or w.endswith(';')
    return ' '.join(out)
E = [(e[0], e[1], title(e[2])) + tuple(e[3:]) for e in E]

ids = {p[0] for p in P}
assert len(ids) == len(P)
for e in E: assert e[1] in ids and e[0] in dict(ERAS), e
used = {e[1] for e in E}
assert used == ids, ids - used
out = {
  'note': 'Places the Gospels record Our Lord going, and the moments of His life in a traditional harmony of the four Gospels. References: New American Bible, Revised Edition. Built by scripts/jesus/build.py.',
  'eras': [{'k': k, 'color': c} for k, c in ERAS],
  'places': [dict(id=i, n=n, m=m, ll=ll, cert=c, s=s, w=w, **({'bp': bp} if bp else {}), z=min(z, 15.5)) for i, n, m, ll, c, s, w, bp, z in P],
  'events': [dict(e=e[0], p=e[1], t=e[2], r=e[3], s=e[4], **({'u': e[5]} if len(e) > 5 else {})) for e in E],
}
root = os.path.join(os.path.dirname(__file__), '..', '..')
with open(os.path.join(root, 'data', 'jesus.json'), 'w', encoding='utf-8') as f: json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
print(len(P), 'places,', len(E), 'events')
