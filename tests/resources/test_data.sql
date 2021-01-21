INSERT INTO users (username, password)
VALUES 
	('test1', 'pbkdf2:sha256:150000$T6VTY461$5440021fa6e7aaefde9b7dcffba88be05717010e6b36790365db661e9177171d'),
	('test2', 'pbkdf2:sha256:150000$N0njVMsP$dafc76a3e82e013b83d6ad02accb97272adc246151a3ae5aa1553e448dcd07aa');

INSERT INTO recipes (name, description, user_id, image_url, url, yield, authors, ingredients, instructions, times, category, keywords)
VALUES
	(
		'Fraisier cake', 
		'An incredibly pretty French cake filled with delicious strawberries and crème pâtissière. Tricky to achieve but certain to impress',
		1, 
		'https://www.bbc.co.uk/food/recipes/fraisier_cake_75507', 
		'https://ichef.bbci.co.uk/food/ic/food_16x9_1600/recipes/fraisier_cake_75507_16x9.jpg',
		'Makes 1 x 23cm/9in cake',
		'["Mary Berry"]',
		'["125g/4½oz caster sugar", "4 free-range eggs", "2 lemons, zest only, finely grated", "125g/4½oz self-raising flour, plus extra for flouring"]',
		'{"type": "steps", "steps": ["Preheat the oven to 180C/350F/Gas 4.", "Grease, flour and line the base of a 23cm/9in spring-form or round loose bottom cake tin.", "Place the sugar, eggs and lemon zest in a large bowl set over a pan of simmering water."]}',
		'{"cook": 7200, "prep": 1800}',
		'["Cakes and baking"]',
		'["mary’s berry", "showstopper bakes", "gâteau", "strawberry", "vegetarian", "The Great British Bake Off"]'
	);