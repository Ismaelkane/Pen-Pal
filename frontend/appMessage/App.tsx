import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import ConversationsScreen from './src/screens/ConversationsScreen';
import MessageDetailScreen from './src/screens/MessageDetailScreen';
import { RootStackParamList } from './src/types/navigation'; // Import types
import LoginScreen from './src/screens/LoginScreen'; // Your login screen component
import SignupScreen from './src/screens/SignupScreen'; 
import SettingScreen from './src/screens/SettingsScreen';
import GroupChatsScreen from './src/screens/GroupChatScreen'; // Adjust the path if needed
import GroupMessageDetailScreen from './src/screens/GroupMessageDetailScreen';
import CreateGroup from './src/screens/CreateGroup';
const Stack = createStackNavigator<RootStackParamList>(); // Typing the stack navigator


const App = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Login">
       <Stack.Screen name="Login" component={LoginScreen} />
       <Stack.Screen name="Signup" component={SignupScreen} />
       <Stack.Screen name="Conversations" component={ConversationsScreen} />
        <Stack.Screen name="MessageDetail" component={MessageDetailScreen} />
        <Stack.Screen name ="SettingScreen" component={SettingScreen} />
        <Stack.Screen name ="GroupChats" component={GroupChatsScreen} />
        <Stack.Screen name ="GroupMessageDetail" component={GroupMessageDetailScreen} />
        <Stack.Screen name ="CreateGroup" component={CreateGroup} />
      </Stack.Navigator>
    </NavigationContainer>
  );
};
export default App;