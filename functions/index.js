const functions = require('firebase-functions');
const admin = require('firebase-admin');
const express = require('express');
const cors = require('cors');
const uuid = require('uuid');

admin.initializeApp();

const app = express();
app.use(cors());

// GET endpoint to return all records from the 'status' table
app.get('/status', async (req, res) => {
	try {
		const snapshot = await admin.database().ref('status').once('value');
		const statuses = snapshot.val();
		res.status(200).send(statuses);
	} catch (error) {
		console.error(error);
		res.status(500).send('Server error');
	}
});

// POST endpoint to update a record in the 'status' table
app.post('/status/:id', async (req, res) => {
	const { id } = req.params;
	const { status } = req.body;
	try {
		await admin.database().ref(`status/${id}`).update({ status });
		res.status(200).send('Status updated successfully');
	} catch (error) {
		console.error(error);
		res.status(500).send('Server error');
	}
});

// POST endpoint to create a new record in the 'status' table
app.post('/status', async (req, res) => {
	const { friendlyName, status, date } = req.body;
	const id = uuid.v4();
	try {
		await admin.database().ref(`status/${id}`).set({ id, friendlyName, status, date });
		res.status(200).send('Status created successfully');
	} catch (error) {
		console.error(error);
		res.status(500).send('Server error');
	}
});

exports.api = functions.https.onRequest(app);
