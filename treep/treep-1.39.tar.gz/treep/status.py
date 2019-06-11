# Treep, copyright 2019 Max Planck Gesellschaft
# Author : Vincent Berenz 

# This file is part of Treep.

#    Treep is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Treep is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Treep.  If not, see <https://www.gnu.org/licenses/>.


from . import coloring


class Status(object):

    __slots__ = [ "repo_name",
                  "path",
                  "origin",
                  "branch",
                  "commit_sha1",
                  "commit_author",
                  "commit_date",
                  "commit_message",
                  "commit_summary",
                  "local_modifications",
                  "status_message",
                  "behind_origin",
                  "ahead_origin",
                  "message",
                  "nb_modified_files"]

    
    def __init__(self):

        for attr in self.__class__.__slots__ :
            setattr(self,attr,None)
        

    def __str__(self):

        return self.repo_name+" ("+str(self.branch)+") "+str(self.origin)


    def pretty_print(self,workspace_path):

        s = ["\t\t"]

        # repository name
        
        s.append( coloring.b_green(self.repo_name) )

        # current branch
        
        if self.branch == "master":
            branch = coloring.b_cyan("master")
        else :
            branch = coloring.b_blue(self.branch)
        s.append( branch )

        # info about status: ahead, behind, number of modified files

        if self.ahead_origin :
            s.append(coloring.b_green("ahead of origin"))
        if self.behind_origin:
            s.append(coloring.b_blue("behind origin"))

        if self.nb_modified_files is not None and self.nb_modified_files>0 :
            if self.nb_modified_files>1: s_='s'
            else : s_=''
            s.append(coloring.b_orange(str(self.nb_modified_files)+" local modification"+s_))
        
        # info about latest commit, if any (could be empty repo)
        
        if self.commit_summary is not None:        

            commit_list = []
            
            if len(self.commit_summary)<=30:
                commit_summary = self.commit_summary
            else :
                commit_summary = self.commit_summary[:30]+" ..."
                
            commit_list.append(str(self.commit_date)+" | ")    
            commit_list.append(self.commit_sha1[:8])
            commit_list.append("'"+str(commit_summary)+"'")

            commit_str = "\n\t\t\t"+" ".join(commit_list)

            s.append(commit_str)
            
        # origin url

        s.append( "\n\t\t\t"+self.origin )

        # path where the repo is cloned

        s.append( "\n\t\t\t"+self.path[len(workspace_path):] )

        # formatted status message, if any
        if self.status_message:
            lines = self.status_message[2:-1].split("\n")
            for line in lines:
                if line:
                    s.append("\n\t\t\t\t"+coloring.cyan(line))

        
        print (" ".join([str(a) for a in s]))
        


def pretty_print(statuses,workspace_path):

    print("\n\t"+coloring.b_green("STATUS"))
    
    statuses_ = sorted(statuses,key = lambda status: status.repo_name)

    print ("")
    
    for status in statuses_:
        status.pretty_print(workspace_path)

    print("")
    
    
