angular.module('myApp')
  .controller('ChatController', ['$scope', '$location', '$rootScope', '$http', '$route', '$cookies',
  function($scope, $location, $rootScope, $http, $route, $cookies) {
      $scope.message = null;
      $scope.ready = false;
      var token = $cookies.get('token');

      $scope.lastMessageId = null;
      $scope.history = [];

      socket = $rootScope.socket = io.connect({
        'reconnection': true,
        'reconnectionDelay': 500,
        'reconnectionAttempts': 1000,
        'query': {token}
      });

      $scope.scrollToBottom = function(){
        var obj = document.getElementById('chat');
        obj.scrollTop = obj.scrollHeight;
      }

      $scope.sendMessage = function(){
        if(!$scope.message.trim()){
            return;
        }

        data = {
            token,
            'text': $scope.message
        };

        socket.emit('message', data);
        $scope.message = '';
      }

      $scope.onLogout = function(data){
        $cookies.remove('token');
        $location.path('/');
        $scope.$apply();
      };

      $scope.onNewMessage = function(data){
        var newMessageId = data.data.id;

        if($scope.lastMessageId && (newMessageId === $scope.lastMessageId + 1)){
            $scope.lastMessageId = newMessageId;
            $scope.history.push(data.data);

            $scope.$apply();

            $scope.scrollToBottom();
        }
        else{
            $scope.lastMessageId = null;
            socket.emit('history', {token});
        }
      };

      $scope.onNewHistory = function(data){
        $scope.history = data.data;

        if($scope.history.length){
            $scope.lastMessageId = $scope.history[$scope.history.length - 1].id;
        }

        $scope.$apply();
        $scope.scrollToBottom();
      };

      socket.on('connect', function () {
          socket.on('logout', $scope.onLogout);
          socket.on('new_message', $scope.onNewMessage);
          socket.on('new_history', $scope.onNewHistory);

          socket.emit('history', {token});
          $scope.ready = true;
      });

       socket.on('connect_error', function(err) {
          if(err.description === 401){  // unauthorized
            socket.disconnect();
            $scope.onLogout();
          }
        });
  }]);