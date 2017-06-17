from datetime import datetime
from .response import Response


class Request(object):
    """
        A statement represents a single spoken entity, sentence or
        phrase that someone can say.
        """
    def __init__(self,text,**kwargs):

        # Try not to allow non-string types to be passed to statements
        try:
            text = str(text)
        except UnicodeEncodeError:
            pass
        #if kwargs.get('image') and not kwargs.get('image').isspace():
            #self.image=kwargs.get('image')
        #else:
            #self.image=''

        self.text = text
        self.in_response_to = kwargs.pop('in_translate_to', [])

        # The date and time that this statement was created at
        self.created_at = kwargs.pop('created_at', datetime.now())

        self.extra_data = kwargs.pop('extra_data', {})

        # This is the confidence with which the chat bot believes
        # this is an accurate response. This value is set when the
        # statement is returned by the chat bot.
        self.confidence = 0

        self.storage = None

    def __str__(self):
        return self.text
    def __hash__(self):
        return hash(self.text)
    def __repr__(self):
        return '<Statement text:%s>' % (self.text)

    def __eq__(self, other):
        if not other:
            return False

        if isinstance(other, Request):
            return self.text == other.text

        return self.text == other

    def save(self):
        """
        Save the requesttext in the database.
        """
        self.storage.update(self)

    def add_extra_data(self, key, value):
        """
        This method allows additional data to be stored on the requestext object.

        Typically this data is something that pertains just to this statement.
        For example, a value stored here might be the tagged parts of speech for
        each word in the statement text.

            - key = 'pos_tags'
            - value = [('Now', 'RB'), ('for', 'IN'), ('something', 'NN'), ('different', 'JJ')]

        :param key: The key to use in the dictionary of extra data.
        :type key: str

        :param value: The value to set for the specified key.
        """
        self.extra_data[key] = value

    def add_response(self,response):
        """
                Add the response to the list of statements that this statement is in response to.
                If the response is already in the list, increment the occurrence count of that response.

                :param response: The response to add.
                :type response: `Response`
            """

        if not isinstance(response, Response):
            raise Request.InvalidTypeException(
                'A {} was recieved when a {} instance was expected'.format(
                    type(response),
                    type(Response(''))
                )
            )


        updated = False

        for i in range(len(self.in_response_to)):
            if response.text==self.in_response_to[i].text:
                self.in_response_to[i].occurrence += 1
                updated=True
        if not updated:
            self.in_response_to.append(response)

    def remove_response(self, response_text):
        """
        Removes a response from the statement's response list based
        on the value of the response text.

        :param response_text: The text of the response to be removed.
        :type response_text: str
        """
        for response in self.in_response_to:
            if response_text == response.text:
                self.in_response_to.remove(response)
                return True
        return False

    def get_response_count(self, requesttext):
        """
        Find the number of times that the statement has been used
        as a response to the current statement.

        :param statement: The statement object to get the count for.
        :type statement: `Statement`

        :returns: Return the number of times the statement has been used as a response.
        :rtype: int
        """
        for response in self.in_response_to:
            if requesttext.text == response.text:
                return response.occurrence

        return 0

    def serialize(self):
        """
        :returns: A dictionary representation of the statement object.
        :rtype: dict
        """
        data = {}

        data['text'] = self.text
        data['in_translate_to'] = []
        data['created_at'] = self.created_at
        data['extra_data'] = self.extra_data

        for response in self.in_response_to:
            data['in_translate_to'].append(response.serialize())

        return data

    class InvalidTypeException(Exception):

        def __init__(self, value='Recieved an unexpected value type.'):
            self.value = value

        def __str__(self):
            return repr(self.value)