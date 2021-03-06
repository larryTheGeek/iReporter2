import smtplib
import os

from flask import jsonify, request, current_app
from flask_restful import Resource, reqparse
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.utils import secure_filename

from app.api.v2.models.incidentmodels import IncidentModels
from app.api.v2.models.usermodels import UserModels

parser = reqparse.RequestParser()
parser.add_argument(
    "typeofincident", type=str, required=True, help="Type field is required")
parser.add_argument(
    "description", type=str, required=True, help="Description field is required")
parser.add_argument(
    "location", type=str, required=True, help="Location field is required")
parser2 = reqparse.RequestParser()
parser2.add_argument(
    "location", type=str, required=True, help="Location field is required")
parser3 = reqparse.RequestParser()
parser3.add_argument(
    "description", type=str, required=True, help="Description field is required")
parser4 = reqparse.RequestParser()
parser4.add_argument(
    "status", type=str, required=True, help="Status field is required")


class Incidents(Resource):
    """Handles creation of new incidents in the system by the users
    Also handles getting of all incidents in the database"""

    def __init__(self):
        self.db = IncidentModels()

    @jwt_required
    def post(self):

        data = parser.parse_args()
        created_by = get_jwt_identity()
        typeofincident = data['typeofincident']
        description = data['description']
        location = data['location']
        file = request.files['file']

        if not os.path.isdir(current_app.config['UPLOAD_FOLDER']):
            os.mkdir(current_app.config['UPLOAD_FOLDER'])
        filename = secure_filename(file.filename)
        filepath = os.path.join(
            current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        resp = None
        if self.db.validate_comment(description) == False:
            resp = {'Error': 'Comment cannot contain special characters!'}
        if typeofincident.isspace() or typeofincident == "":
            resp = {'Error': 'Type cannot be empty!'}
        if description.isspace() or description == "":
            resp = {'Error': 'Description cannot be empty!'}
        if location.isspace() or location == "":
            resp = {'Error': 'Location cannot be empty!'}
        if resp is not None:
            return jsonify(resp)

        self.db.save_incident(created_by, typeofincident,
                              description, location, filepath)
        return {
            'Message': 'Record successfully saved!'
        }, 201

    def get(self):

        result = self.db.get_all()

        if result == []:
            return {
                'Error': 'No record found!'
            }, 404
        else:
            return jsonify(
                {
                    'Message': 'Records returned successfully',
                    'Data': result
                }, 200)


class Incident(Resource):
    """Handles deleting and finding an incident using its id."""

    def __init__(self):
        self.db = IncidentModels()

    @jwt_required
    def delete(self, incidenttype, incident_id):
        userincidents = self.db.get_by_user_id(get_jwt_identity(), incident_id)
        if not self.db.get_from_type_by_id(incidenttype, incident_id):
            return {
                'Error': 'The record you are trying to delete has not been found!'
            }, 404
        if not userincidents:
            return{
                'Error': 'You cannot delete an incident that does not belong to you!'
            }, 401
        if userincidents['status'] != 'DRAFT':
            return {
                'Error': 'Incident status already changed. You cannot delete this incident!'
            }, 403
        self.db.delete(incident_id, get_jwt_identity())
        return {
            'Message': 'Record successfully deleted!',
            'data': [
                {
                    "id": incident_id
                }
            ]
        }, 200

    @jwt_required
    def get(self, incidenttype, incident_id):
        incident = self.db.get_from_type_by_id(incidenttype, incident_id)
        if incident == []:
            return {
                'Error': 'Record not found!'
            }, 404
        return jsonify({
            'Message': 'Record returned successfully',
            'Data': incident
        }, 200)


class Type(Resource):
    """Handles fetching incidents by type in the system"""

    def __init__(self):
        self.db = IncidentModels()

    @jwt_required
    def get(self, incidenttype):
        incident = self.db.get_by_type(incidenttype, get_jwt_identity())
        if incident == []:
            return {
                'Error': 'Records not found!'
            }, 404
        return jsonify({
            'Message': 'Records returned successfully',
            'Data': incident
        }, 200)


class Status(Resource):
    """Handles fetching incidents by status in the system"""

    def __init__(self):
        self.db = IncidentModels()

    @jwt_required
    def get(self, status):
        incident = self.db.get_by_status(status, get_jwt_identity())
        if incident == []:
            return {
                'Error': 'Records not found!'
            }, 404
        return jsonify({
            'Message': 'Records returned successfully',
            'Data': incident
        }, 200)


class LocationUpdate(Resource):
    """Handles incident location update by users in the system"""

    def __init__(self):
        self.db = IncidentModels()

    @jwt_required
    def patch(self, incidenttype, incident_id):
        data = parser2.parse_args()
        location = data['location']
        incident = self.db.get_from_type_by_id(incidenttype, incident_id)
        userincidents = self.db.get_by_user_id(get_jwt_identity(), incident_id)
        if not incident:
            return {
                'Error': 'Record not found!'
            }, 404
        if incident[0]['status'] != 'DRAFT':
            return {
                'Error': 'Incident status already changed. You cannot update this incident!'
            }, 403
        if not userincidents:
            return {
                'Error': 'You cannot update an incident that does not belong to you!'
            }, 401
        self.db.updatelocation(location, incident_id, get_jwt_identity())
        return jsonify({
            'Message': 'Updated {} location successfully!'.format(incidenttype),
            'data': [
                {
                    "id": incident_id
                }
            ]
        }, 200)


class CommentUpdate(Resource):
    """Handles incident comment updates by users in the system"""

    def __init__(self):
        self.db = IncidentModels()

    @jwt_required
    def patch(self, incidenttype, incident_id):
        data = parser3.parse_args()
        comment = data['description']
        incident = self.db.get_from_type_by_id(incidenttype, incident_id)
        userincidents = self.db.get_by_user_id(get_jwt_identity(), incident_id)
        if not incident:
            return {
                'Error': 'Record not found!'
            }, 404
        if incident[0]['status'] != 'DRAFT':
            return {
                'Error': 'Incident status already changed. You cannot update this incident!'
            }, 403
        if not userincidents:
            return {
                'Error': 'You cannot update an incident that does not belong to you!'
            }, 401
        self.db.updatecomment(comment, incident_id, get_jwt_identity())
        return jsonify({
            'Message': 'Updated {} comment successfully!'.format(incidenttype),
            'data': [
                {
                    "id": incident_id
                }
            ]
        }, 200)


class MediaUpdate(Resource):
    """Handles media files uploads"""

    def __init__(self):
        self.db = IncidentModels()

    @jwt_required
    def patch(self, incidenttype, incident_id):

        file = request.files['file']

        if file:
            if not os.path.isdir(current_app.config['UPLOAD_FOLDER']):
                os.mkdir(current_app.config['UPLOAD_FOLDER'])
            filename = secure_filename(file.filename)
            filepath = os.path.join(
                current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            incident = self.db.get_from_type_by_id(incidenttype, incident_id)
            userincidents = self.db.get_by_user_id(
                get_jwt_identity(), incident_id)
            if not incident:
                return {
                    'Error': 'Record not found!'
                }, 404
            if incident[0]['status'] != 'DRAFT':
                return {
                    'Error': 'Incident status already changed. You cannot update this incident!'
                }, 403
            if not userincidents:
                return {
                    'Error': 'You cannot update an incident that does not belong to you!'
                }, 401

            self.db.updatemedia(filepath, incident_id, get_jwt_identity())
            return jsonify({
                'Message': 'Updated {} media successfully!'.format(incidenttype),
                'data': [
                    {
                        "id": incident_id
                    }
                ]
            }, 200)

        else:
            return {
                'Error': "No image or video selected!"
            }, 404


class Admin(Resource):
    """Handles admin user functionality. Allows the admin user to
    update incident status. A real time email notification is sent to the user
    once the update is successful"""

    def __init__(self):
        self.db = IncidentModels()
        self.admin = UserModels()

    @jwt_required
    def patch(self, incidenttype, incident_id):
        data = parser4.parse_args()
        status = data['status']
        incident = self.db.get_from_type_by_id(incidenttype, incident_id)
        email = self.db.get_user_email(incident_id)

        if not self.admin.isadmin(get_jwt_identity()):
            return{
                'Error': 'You are not an admin!'
            }, 403
        if not incident:
            return {
                'Error': 'Record not found!'
            }, 404
        self.db.updatestatus(status, incident_id)
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login("issamwangi@gmail.com", "issamwangi")
            msg = 'Your incident status has been changed to {}'.format(status)
            server.sendmail("issamwangi@gmail.com", email, msg)
            server.quit()
        except:
            return jsonify({
                'Message': 'Notification email could not be sent.\
                Check your internet status! Updated incident status successfully!',
                'data': [
                    {
                        "id": incident_id
                    }
                ]
            }, 200)

        return jsonify({
            'Message': 'Updated incident status successfully!',
            'data': [
                {
                    "id": incident_id
                }
            ]
        }, 200)
