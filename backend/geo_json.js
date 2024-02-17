const { MongoClient } = require('mongodb');
const fs = require('fs');

const uri = 'mongodb+srv://projecttidal:sHf2O4p2qv8jgpJ3@projecttidal.q0fm5uw.mongodb.net/?retryWrites=true&w=majority';

const client = new MongoClient(uri);

async function connect() {
    try {
        await client.connect();
        console.log('Connected to MongoDB');

        await queryDataAndCreateDictionary();
    } catch (error) {
        console.error('Error connecting to MongoDB', error);
    } finally {
        await client.close();
        console.log('Connection closed');
    }
}

async function queryDataAndCreateDictionary() {
    try {
        const database = client.db('ProjectTidal');
        const collection = database.collection('Stations');

        const cursor = collection.find({});

        const features = [];

        await cursor.forEach(document => {
            const feature = {"type": "Feature", "geometry": {"type": "Point", "coordinates": [document["long"], document["lat"]]}, "properties": {
                "id": document["id"],
                "wave power": document["wave power"],
                "wind power": document["wind power"],
                "emissions avoided w/ waves": document["emissions avoided w/ waves"],
                "emissions avoided w/ wind": document["emissions avoided w/ wind"]
            }}
            features.push(feature);
        });

        const geojson = {"type": "FeatureCollection", "features": features};
        const jsonContent = JSON.stringify(geojson, null, 2);
        fs.writeFileSync('stations.geojson', jsonContent);
        console.log('JSON file created successfully');
    } catch (error) {
        console.error('Error querying data from MongoDB or writing to file', error);
    }
}

connect();